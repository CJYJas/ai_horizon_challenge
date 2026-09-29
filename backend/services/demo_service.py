import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlmodel import Session
from langchain_core.language_models.chat_models import BaseChatModel

from backend.models import (
    SMEAssessment,
    TopPainPoint,
    Recommendation,
    GovernmentSupportMatch,
    CompanyProfile,
    Answer,
)
from backend.api.schemas import AnswerResponse
from backend.ai_chains.strategist import StrategistOutput
from backend.services.assessment import generate_report, lead_metrics_from_assessment
from backend.solution_matching.matcher import run_solution_matcher
from backend.data_loaders import load_supporting_rules, load_demo_case
from backend.api.lead_helpers import normalize_sales_brief

logger = logging.getLogger(__name__)


def is_demo_assessment(assessment: Optional[SMEAssessment]) -> bool:
    """Check if an assessment is marked as a demo assessment."""
    if not assessment:
        return False
    if assessment.assessment_id.startswith("demo-"):
        return True
    if (assessment.business_context or {}).get("is_demo"):
        return True
    return False


def get_demo_scenario() -> Dict[str, Any]:
    """Return the canonical demo case configuration."""
    return load_demo_case()


def create_demo_assessment(db: Session, custom_profile: Optional[Dict[str, Any]] = None) -> SMEAssessment:
    """Create a new demo assessment pre-seeded with ABC Enterprise profile in SQLite."""
    demo_case = load_demo_case()
    profile = demo_case["company_profile"].copy()
    if custom_profile:
        profile.update(custom_profile)

    new_id = f"demo-{uuid.uuid4().hex[:8]}"
    assessment = SMEAssessment(
        assessment_id=new_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        company_profile=profile,
        business_context={"is_demo": True},
        answers=[],
        diagnosis={},
        maturity_scores={},
        impact_simulation={},
        recommendations=[],
        government_support=[],
        lead_score=0.0,
        lead_score_reasons=[],
        sales_brief={},
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    logger.info("Created demo assessment with ID %s", new_id)
    return assessment


def handle_demo_answer(
    assessment: SMEAssessment,
    answer_text: str,
    question_text: Optional[str] = None,
    question_topic: Optional[str] = None,
    db: Optional[Session] = None,
) -> AnswerResponse:
    """
    Handle an answer in Demo Mode.
    Follows canonical 3-turn sequence from docs/mock_flow.md without relying on unstable LLM loops.
    """
    demo_case = load_demo_case()
    dialogue_steps = demo_case.get("dialogue_steps", [])

    answers = list(assessment.answers or [])
    new_step_num = len(answers) + 1

    new_answer = Answer(
        question_id=f"q_{new_step_num}",
        question_text=question_text or f"Demo question {new_step_num}",
        question_topic=question_topic or "adaptive",
        answer=answer_text,
        asked_reason="Demo controlled scenario",
    )
    answers.append(new_answer.model_dump())
    assessment.answers = answers

    # Dialogue progression
    if new_step_num == 1:
        # Step 1 answered -> ask Question 2 (hours spent)
        next_step = next((s for s in dialogue_steps if s.get("step") == 1), None)
        q_text = next_step["question_text"] if next_step else "How many hours per week does your team spend handling customer enquiries and orders?"
        reason = next_step.get("reason", "Workload quantification") if next_step else "Workload quantification"
        topic = next_step.get("question_topic", "workload") if next_step else "workload"

        if db:
            db.add(assessment)
            db.commit()

        return AnswerResponse(
            is_complete=False,
            follow_up_question=q_text,
            reason=reason,
            question_topic=topic,
        )

    elif new_step_num == 2:
        # Step 2 answered -> ask Question 3 (lost orders / WhatsApp fragmentation)
        next_step = next((s for s in dialogue_steps if s.get("step") == 2), None)
        q_text = next_step["question_text"] if next_step else "Do you lose enquiries or orders because multiple staff members handle WhatsApp messages separately?"
        reason = next_step.get("reason", "Channel fragmentation check") if next_step else "Channel fragmentation check"
        topic = next_step.get("question_topic", "outcome") if next_step else "outcome"

        if db:
            db.add(assessment)
            db.commit()

        return AnswerResponse(
            is_complete=False,
            follow_up_question=q_text,
            reason=reason,
            question_topic=topic,
        )

    else:
        # Step 3+ answered -> assessment complete
        hypotheses = demo_case.get("diagnosis", {}).get(
            "hypotheses",
            ["Customer-order management bottleneck across WhatsApp and spreadsheets"],
        )
        assessment.diagnosis = {**(assessment.diagnosis or {}), "hypotheses": hypotheses}
        if db:
            db.add(assessment)
            db.commit()

        return AnswerResponse(is_complete=True)


def generate_demo_diagnosis(
    assessment: SMEAssessment,
    db: Session,
    llm: Optional[BaseChatModel] = None,
) -> Dict[str, Any]:
    """
    Generate diagnosis for Demo Mode.
    Reuses existing deterministic scoring, product matcher, and government programme matcher.
    If LLM is available, enriches explanation; otherwise uses canonical demo explanations safely.
    """
    rules = load_supporting_rules().model_dump()
    demo_case = load_demo_case()

    # Load canonical pain points
    raw_pain_points = demo_case.get("diagnosis", {}).get("pain_points", [])
    pain_points: List[TopPainPoint] = []
    for rank, p in enumerate(raw_pain_points, start=1):
        pain_points.append(
            TopPainPoint(
                problem=p["problem"],
                root_cause=p["root_cause"],
                evidence=p.get("evidence", [a.get("answer", "") for a in (assessment.answers or [])]),
                business_impact=p["business_impact"],
                impact_estimate=p.get("impact_estimate", "26000"),
                urgency=p.get("urgency", "medium"),
                priority_rank=p.get("priority_rank", rank),
            )
        )

    # Real deterministic scoring calculations
    metrics = lead_metrics_from_assessment(assessment, rules)

    # Update impact_estimate and urgency with real calculated values
    for pt in pain_points:
        pt.urgency = metrics["urgency"]
        if metrics["impact_cost"] is not None:
            pt.impact_estimate = str(metrics["impact_cost"])

    # Real product and government support matcher
    profile_model = CompanyProfile(**assessment.company_profile)
    matches = run_solution_matcher(pain_points, profile_model)

    # Enrich recommendations with clean reason
    for rec in matches.get("recommendations", []):
        if not rec.reason or rec.reason.startswith("Matched"):
            rec.reason = (
                f"Matched {rec.product_id.capitalize()} to centralise customer communication, "
                "eliminate manual order tracking errors, and prevent missed customer enquiries."
            )

    diagnosis_data = {
        "pain_points": [p.model_dump() for p in pain_points],
        "maturity_scores": metrics["mat_scores"],
        "recommendations": [r.model_dump() for r in matches["recommendations"]],
        "government_support": [g.model_dump() for g in matches["government_support"]],
        "lead_score": metrics["lead_score"],
        "lead_score_reasons": metrics["lead_score_reasons"],
        "overall_priority": metrics["priority"],
    }

    # Persist in DB
    assessment.diagnosis = {
        **(assessment.diagnosis or {}),
        "pain_points": diagnosis_data["pain_points"],
        "overall_priority": diagnosis_data["overall_priority"],
    }
    assessment.maturity_scores = diagnosis_data["maturity_scores"]
    assessment.recommendations = diagnosis_data["recommendations"]
    assessment.government_support = diagnosis_data["government_support"]
    assessment.lead_score = diagnosis_data["lead_score"]
    assessment.lead_score_reasons = diagnosis_data["lead_score_reasons"]

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return diagnosis_data


def generate_demo_report(
    assessment: SMEAssessment,
    db: Session,
    llm: Optional[BaseChatModel] = None,
) -> StrategistOutput:
    """
    Generate or retrieve Strategist report for Demo Mode.
    Uses canonical demo report structure to guarantee 100% reliable hackathon presentation.
    """
    cached_report = (assessment.diagnosis or {}).get("narrative_report")
    if cached_report:
        return StrategistOutput(**cached_report)

    demo_case = load_demo_case()
    raw_report = demo_case.get("report", {})
    report = StrategistOutput(**raw_report)

    # Persist in DB
    assessment.diagnosis = {
        **(assessment.diagnosis or {}),
        "narrative_report": report.model_dump(),
    }
    assessment.lead_score_reasons = report.sales_brief.why_this_lead_is_hot

    stored_pain_points = assessment.diagnosis.get("pain_points", [])
    pain_points = [TopPainPoint(**p) for p in stored_pain_points]
    recs = [Recommendation(**r) for r in assessment.recommendations]

    assessment.sales_brief = normalize_sales_brief(
        report.sales_brief.model_dump(),
        assessment.company_profile,
        pain_points,
        report.sales_brief.why_this_lead_is_hot,
        recs,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return report
