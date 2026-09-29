from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.api.dependencies import get_session
from backend.api.schemas import (
    CreateAssessmentRequest,
    CreateAssessmentResponse,
    AnswerRequest,
    AnswerResponse,
    DiagnosisResponse,
    ImpactSimulationRequest,
    ImpactSimulationResponse,
    ReportResponse,
)
from backend.models import (
    SMEAssessment,
    TopPainPoint,
    Recommendation,
    GovernmentSupportMatch,
    CompanyProfile,
)
from backend.services.demo_service import (
    get_demo_scenario,
    create_demo_assessment,
    handle_demo_answer,
    generate_demo_diagnosis,
    generate_demo_report,
)
from backend.services.assessment import lead_metrics_from_assessment
from backend.scoring.engine import calculate_impact
from backend.data_loaders import load_supporting_rules

demo_router = APIRouter(prefix="/demo", tags=["Demo"])


@demo_router.get("/case")
def get_demo_case_info():
    """Retrieve canonical demo scenario configuration."""
    return get_demo_scenario()


@demo_router.post("/assessments", response_model=CreateAssessmentResponse)
def start_demo_assessment(
    req: Optional[CreateAssessmentRequest] = None,
    db: Session = Depends(get_session),
):
    """
    Start a controlled Demo assessment pre-seeded with ABC Enterprise profile
    (or custom override).
    """
    custom_profile = req.company_profile.model_dump() if req else None
    assessment = create_demo_assessment(db, custom_profile)

    demo_case = get_demo_scenario()
    initial_step = demo_case.get("dialogue_steps", [{}])[0]
    initial_q = initial_step.get(
        "question_text",
        "Which tools, apps, or manual steps do you currently use to run your most important daily workflow?",
    )
    initial_topic = initial_step.get("question_topic", "tools_workflow")

    return CreateAssessmentResponse(
        assessment_id=assessment.assessment_id,
        status="Created (Demo Mode)",
        initial_question=initial_q,
        initial_question_topic=initial_topic,
    )


@demo_router.post("/assessments/{id}/answers", response_model=AnswerResponse)
def submit_demo_answer(
    id: str,
    req: AnswerRequest,
    db: Session = Depends(get_session),
):
    """
    Submit an answer in Demo Mode.
    Advances through the canonical 3-question sequence reliably without LLM failures.
    """
    assessment = db.get(SMEAssessment, id)
    if not assessment:
        # Auto-recover demo assessment if session was lost
        assessment = create_demo_assessment(db)

    return handle_demo_answer(
        assessment=assessment,
        answer_text=str(req.answer),
        question_text=req.question_text,
        question_topic=req.question_topic,
        db=db,
    )


@demo_router.get("/assessments/{id}/diagnosis", response_model=DiagnosisResponse)
def get_demo_diagnosis(
    id: str,
    db: Session = Depends(get_session),
):
    """
    Compute diagnosis for Demo assessment.
    Runs real deterministic maturity, urgency, product matching (Freshsales), and grant matching (SFSME 2.0).
    """
    assessment = db.get(SMEAssessment, id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Demo assessment not found")

    stored_pain_points = (assessment.diagnosis or {}).get("pain_points", [])
    if stored_pain_points and assessment.recommendations and assessment.maturity_scores:
        narrative = assessment.diagnosis.get("narrative_report") or {}
        return DiagnosisResponse(
            top_pain_points=[TopPainPoint(**p) for p in stored_pain_points],
            maturity_scores=assessment.maturity_scores,
            recommendations=[Recommendation(**r) for r in assessment.recommendations],
            government_support=[GovernmentSupportMatch(**g) for g in assessment.government_support],
            lead_score=assessment.lead_score,
            maturity_gap_explanation=narrative.get("maturity_gap_explanation"),
        )

    diag_data = generate_demo_diagnosis(assessment, db)
    return DiagnosisResponse(
        top_pain_points=[TopPainPoint(**p) for p in diag_data["pain_points"]],
        maturity_scores=diag_data["maturity_scores"],
        recommendations=[Recommendation(**r) for r in diag_data["recommendations"]],
        government_support=[GovernmentSupportMatch(**g) for g in diag_data["government_support"]],
        lead_score=diag_data["lead_score"],
        maturity_gap_explanation=None,
    )


@demo_router.post("/assessments/{id}/impact-simulation", response_model=ImpactSimulationResponse)
def simulate_demo_impact(
    id: str,
    req: ImpactSimulationRequest,
    db: Session = Depends(get_session),
):
    """
    Run impact simulation on Demo assessment using real deterministic formulas.
    Default inputs (20 hrs, RM25/hr, 50%) yield RM26,000 cost and RM13,000 recovered value,
    updating lead score to 70.74 and priority to 2.
    """
    assessment = db.get(SMEAssessment, id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Demo assessment not found")

    rules = load_supporting_rules().model_dump()
    annual_cost = calculate_impact(req.hours_per_week, req.hourly_rate_assumption, rules)
    weeks_per_year = rules.get("impact_simulation", {}).get("weeks_per_year", 52)
    hours_per_year = req.hours_per_week * weeks_per_year
    recovered_hours = hours_per_year * (req.automation_scenario_pct / 100.0)
    recovered_value = recovered_hours * req.hourly_rate_assumption

    sim_data = {
        "input_hours_per_week": req.hours_per_week,
        "hourly_rate_assumption": req.hourly_rate_assumption,
        "annual_opportunity_cost": annual_cost,
        "automation_scenario_pct": req.automation_scenario_pct,
        "recovered_hours_per_year": recovered_hours,
        "recovered_value_per_year": recovered_value,
    }

    assessment.impact_simulation = sim_data
    metrics = lead_metrics_from_assessment(assessment, rules)
    assessment.lead_score = metrics["lead_score"]
    if assessment.diagnosis is not None:
        assessment.diagnosis = {
            **assessment.diagnosis,
            "overall_priority": metrics["priority"],
            "narrative_report": None,
        }

    db.add(assessment)
    db.commit()

    return ImpactSimulationResponse(**sim_data)


@demo_router.get("/assessments/{id}/report", response_model=ReportResponse)
def get_demo_report(
    id: str,
    db: Session = Depends(get_session),
):
    """
    Generate or return report for Demo assessment with guaranteed fallback to canonical demo report.
    """
    assessment = db.get(SMEAssessment, id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Demo assessment not found")

    # If diagnosis has not been executed yet, run it
    if not assessment.recommendations or not assessment.maturity_scores:
        generate_demo_diagnosis(assessment, db)

    report = generate_demo_report(assessment, db)

    stored_pain_points = (assessment.diagnosis or {}).get("pain_points", [])
    pain_points = [TopPainPoint(**p) for p in stored_pain_points]
    recs = [Recommendation(**r) for r in assessment.recommendations]
    govs = [GovernmentSupportMatch(**g) for g in assessment.government_support]

    diag_resp = DiagnosisResponse(
        top_pain_points=pain_points,
        maturity_scores=assessment.maturity_scores,
        recommendations=recs,
        government_support=govs,
        lead_score=assessment.lead_score,
        maturity_gap_explanation=report.maturity_gap_explanation,
    )

    return ReportResponse(
        report=report,
        company_profile=CompanyProfile(**assessment.company_profile),
        diagnosis_data=diag_resp,
        impact_simulation=assessment.impact_simulation or None,
    )
