import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from backend.api.dependencies import get_session, get_llm
from backend.api.schemas import (
    CreateAssessmentRequest, CreateAssessmentResponse,
    AnswerRequest, AnswerResponse, DiagnosisResponse,
    ImpactSimulationRequest, ImpactSimulationResponse,
    ReportResponse, SalesReportResponse, LeadCardResponse, LeadDetailResponse
)
from backend.models import SMEAssessment, TopPainPoint, Recommendation, GovernmentSupportMatch, CompanyProfile, Answer
from backend.ai_chains.analyst import run_analyst_loop, run_diagnosis_chain, classify_question_topic
from backend.ai_chains.strategist import run_strategist, StrategistOutput
from backend.services.assessment import generate_diagnosis, generate_report, lead_metrics_from_assessment
from backend.scoring.engine import (
    calculate_maturity_scores, calculate_weighted_maturity,
    calculate_impact, classify_impact, classify_urgency, derive_urgency_signals,
    calculate_priority, calculate_lead_score, generate_lead_score_reasons
)
from backend.solution_matching.matcher import run_solution_matcher
from backend.data_loaders import load_exabytes_products, load_supporting_rules
from backend.api.lead_helpers import format_lead_label, normalize_sales_brief

router = APIRouter()


def _opening_question(profile: dict) -> str:
    """Open on operational context, never profile fields already collected."""
    return "Which tools, apps, or manual steps do you currently use to run your most important daily workflow?"

@router.post("/assessments", response_model=CreateAssessmentResponse)
def create_assessment(req: CreateAssessmentRequest, db: Session = Depends(get_session)):
    new_id = str(uuid.uuid4())
    assessment = SMEAssessment(
        assessment_id=new_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        company_profile=req.company_profile.model_dump(),
        answers=[],
        diagnosis={},
        maturity_scores={},
        impact_simulation={},
        recommendations=[],
        government_support=[],
        lead_score=0.0,
        lead_score_reasons=[]
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return CreateAssessmentResponse(
        assessment_id=assessment.assessment_id,
        status="Created",
        initial_question=_opening_question(assessment.company_profile),
        initial_question_topic="tools_workflow",
    )

@router.post("/assessments/{id}/answers", response_model=AnswerResponse)
def add_answer(id: str, req: AnswerRequest, db: Session = Depends(get_session), llm = Depends(get_llm)):
    assessment = db.get(SMEAssessment, id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    # Append answer
    answers = list(assessment.answers or [])
    new_answer = Answer(
        question_id=f"q_{len(answers)+1}",
        question_text=req.question_text or f"Assessment response {len(answers)+1}",
        question_topic=req.question_topic or classify_question_topic(req.question_text or ""),
        answer=req.answer,
        asked_reason="Dynamic"
    )
    answers.append(new_answer.model_dump())
    
    # Run analyst chain to see if gap exists
    try:
        output, _ = run_analyst_loop(
            llm=llm,
            company_profile=assessment.company_profile,
            initial_answers=answers,
            max_questions=10,
            ask_user_func=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI analysis failed")
        
    # Update state
    assessment.answers = answers
    db.add(assessment)
    db.commit()
    
    if output.information_gap.exists and output.information_gap.follow_up_question:
        return AnswerResponse(
            is_complete=False,
            follow_up_question=output.information_gap.follow_up_question,
            reason=output.information_gap.reason,
            question_topic=classify_question_topic(output.information_gap.follow_up_question),
        )
    else:
        # Save hypotheses as basic diagnosis text
        assessment.diagnosis = {"hypotheses": output.hypotheses}
        db.add(assessment)
        db.commit()
        return AnswerResponse(is_complete=True)

@router.get("/assessments/{id}/diagnosis", response_model=DiagnosisResponse)
def get_diagnosis(id: str, db: Session = Depends(get_session), llm = Depends(get_llm)):
    assessment = db.get(SMEAssessment, id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Diagnosis is a completed artifact, not a prompt to regenerate on every
    # browser refresh. Reuse it so report and sales views stay consistent.
    stored_pain_points = (assessment.diagnosis or {}).get("pain_points", [])
    if stored_pain_points and assessment.recommendations and assessment.maturity_scores:
        return DiagnosisResponse(
            top_pain_points=[TopPainPoint(**point) for point in stored_pain_points],
            maturity_scores=assessment.maturity_scores,
            recommendations=[Recommendation(**recommendation) for recommendation in assessment.recommendations],
            government_support=[GovernmentSupportMatch(**support) for support in assessment.government_support],
            lead_score=assessment.lead_score,
            maturity_gap_explanation=(assessment.diagnosis.get("narrative_report") or {}).get("maturity_gap_explanation")
        )
        
    # Run core diagnosis logic via service layer
    diagnosis_data = generate_diagnosis(assessment, llm)
    
    # Update assessment state
    assessment.diagnosis = {
        **assessment.diagnosis,
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
    
    return DiagnosisResponse(
        top_pain_points=[TopPainPoint(**p) for p in diagnosis_data["pain_points"]],
        maturity_scores=diagnosis_data["maturity_scores"],
        recommendations=[Recommendation(**r) for r in diagnosis_data["recommendations"]],
        government_support=[GovernmentSupportMatch(**g) for g in diagnosis_data["government_support"]],
        lead_score=diagnosis_data["lead_score"],
        maturity_gap_explanation=None
    )

@router.post("/assessments/{id}/impact-simulation", response_model=ImpactSimulationResponse)
def simulate_impact(id: str, req: ImpactSimulationRequest, db: Session = Depends(get_session)):
    assessment = db.get(SMEAssessment, id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    rules = load_supporting_rules().model_dump()
    annual_cost = calculate_impact(req.hours_per_week, req.hourly_rate_assumption, rules)
    
    # Recalculate recovered value based on pct
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
        "recovered_value_per_year": recovered_value
    }
    
    # PER PLAN FEEDBACK: Overwrite state in DB
    assessment.impact_simulation = sim_data

    rules = load_supporting_rules().model_dump()
    metrics = lead_metrics_from_assessment(assessment, rules)
    assessment.lead_score = metrics["lead_score"]
    # Preserve the generated, lead-specific sales talking points. A simulation
    # changes the score, not the diagnosis behind the sales conversation.
    if not assessment.sales_brief:
        assessment.lead_score_reasons = metrics["lead_score_reasons"]
    if assessment.diagnosis is not None:
        assessment.diagnosis = {
            **assessment.diagnosis,
            "overall_priority": metrics["priority"],
            # A changed impact model deserves a newly grounded narrative on
            # the next report request.
            "narrative_report": None,
        }

    db.add(assessment)
    db.commit()
    
    return ImpactSimulationResponse(**sim_data)

@router.get("/assessments/{id}/report", response_model=ReportResponse)
def get_report(id: str, db: Session = Depends(get_session), llm = Depends(get_llm)):
    assessment = db.get(SMEAssessment, id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    # We must have recommendations from the diagnosis endpoint to run strategist
    if not assessment.recommendations:
        raise HTTPException(status_code=400, detail="Must run /diagnosis before generating report")
        
    # Retrieve pain points
    stored_pain_points = assessment.diagnosis.get("pain_points", [])
    if stored_pain_points:
        pain_points = [TopPainPoint(**p) for p in stored_pain_points]
    else:
        pain_points = [
            TopPainPoint(
                problem=assessment.diagnosis.get("hypotheses", ["Operational bottleneck"])[0],
                root_cause="Fragmented tools",
                evidence=["User answers"],
                business_impact="High",
                impact_estimate="20800",
                urgency="high",
                priority_rank=1
            )
        ]
        
    recs = [Recommendation(**r) for r in assessment.recommendations]
    govs = [GovernmentSupportMatch(**g) for g in assessment.government_support]
    
    sim = assessment.impact_simulation or {}
    impact_cost = sim.get("annual_opportunity_cost")
    
    cached_report = (assessment.diagnosis or {}).get("narrative_report")
    if cached_report:
        report = StrategistOutput(**cached_report)
    else:
        # Generate the report via the service layer
        report = generate_report(assessment, llm)
        assessment.diagnosis = {**assessment.diagnosis, "narrative_report": report.model_dump()}
        
    # Save the sales brief reasons and the full brief to DB (with display-friendly fields)
    assessment.lead_score_reasons = report.sales_brief.why_this_lead_is_hot
    assessment.sales_brief = normalize_sales_brief(
        report.sales_brief.model_dump(),
        assessment.company_profile,
        pain_points,
        report.sales_brief.why_this_lead_is_hot,
        recs,
    )
    db.add(assessment)
    db.commit()
    
    # Construct complete report response
    diag_resp = DiagnosisResponse(
        top_pain_points=pain_points,
        maturity_scores=assessment.maturity_scores,
        recommendations=recs,
        government_support=govs,
        lead_score=assessment.lead_score,
        maturity_gap_explanation=report.maturity_gap_explanation
    )
    
    return ReportResponse(
        report=report,
        company_profile=assessment.company_profile,
        diagnosis_data=diag_resp,
        impact_simulation=assessment.impact_simulation
    )

@router.get("/leads/{id}/sales-report", response_model=SalesReportResponse)
def get_sales_report(id: str, db: Session = Depends(get_session), llm = Depends(get_llm)):
    """Full consultative playbook for authorised sales users."""
    assessment = db.get(SMEAssessment, id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Lead not found")
    report_response = get_report(id, db, llm)
    return SalesReportResponse(
        assessment_id=assessment.assessment_id,
        lead_label=format_lead_label(assessment.company_profile, assessment.assessment_id),
        **report_response.model_dump(),
    )

@router.get("/leads", response_model=List[LeadCardResponse])
def get_leads(db: Session = Depends(get_session)):
    assessments = db.exec(select(SMEAssessment).order_by(SMEAssessment.lead_score.desc())).all()
    
    leads = []
    for a in assessments:
        # The sales workspace promises a usable diagnosis and full report.
        # Keep in-progress assessments in the user flow until those artifacts
        # exist, instead of showing a row that cannot open its details.
        if not a.recommendations or not a.maturity_scores:
            continue
        problem = None
        priority = 0
        rec_trans = None
        
        # Use first recommendation's linked product or transformation
        if a.recommendations and len(a.recommendations) > 0:
            rec_trans = a.recommendations[0].get("product_id", "Digital Solution")
            
        # Get problem and priority from diagnosis top pain points if available
        pain_points = a.diagnosis.get("pain_points", [])
        priority = (a.diagnosis or {}).get("overall_priority")
        if pain_points:
            problem = pain_points[0].get("problem")
            if priority is None:
                priority = pain_points[0].get("priority_rank", 3)
        else:
            hypotheses = a.diagnosis.get("hypotheses", ["Operational bottleneck"]) if a.diagnosis else ["Operational bottleneck"]
            problem = hypotheses[0] if hypotheses else None
            if priority is None:
                priority = 3
        
        # Calculate overall maturity
        scores = a.maturity_scores or {}
        overall = sum(scores.values()) / len(scores) if scores else 0.0

        leads.append(LeadCardResponse(
            assessment_id=a.assessment_id,
            company_name=a.company_profile.get("company_name") or format_lead_label(a.company_profile, a.assessment_id),
            lead_label=format_lead_label(a.company_profile, a.assessment_id),
            company_industry=a.company_profile.get("industry", "Unknown"),
            employee_count=a.company_profile.get("employee_count", 0),
            overall_maturity=overall,
            lead_score=a.lead_score,
            priority=priority,
            top_pain_point_problem=problem,
            recommended_transformation=rec_trans,
            created_at=a.created_at,
            email=a.company_profile.get("email"),
            phone=a.company_profile.get("phone"),
            company_profile=a.company_profile
        ))
    return leads

@router.get("/leads/{id}", response_model=LeadDetailResponse)
def get_lead_detail(id: str, db: Session = Depends(get_session)):
    a = db.get(SMEAssessment, id)
    if not a:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # Reconstruct DiagnosisResponse
    stored_pain_points = a.diagnosis.get("pain_points", [])
    if stored_pain_points:
        pain_points = [TopPainPoint(**p) for p in stored_pain_points]
    else:
        hypotheses = a.diagnosis.get("hypotheses", ["Operational bottleneck"]) if a.diagnosis else ["Operational bottleneck"]
        sim = a.impact_simulation or {}
        impact_cost = sim.get("annual_opportunity_cost", 0.0)
        pain_points = [
            TopPainPoint(
                problem=hypotheses[0],
                root_cause="Fragmented tools",
                evidence=["User assessment responses"],
                business_impact="Revenue and productivity leak",
                impact_estimate=str(impact_cost),
                urgency="high",
                priority_rank=1
            )
        ]
    
    recs = [Recommendation(**r) for r in a.recommendations] if a.recommendations else []
    govs = [GovernmentSupportMatch(**g) for g in a.government_support] if a.government_support else []
    
    diag_resp = DiagnosisResponse(
        top_pain_points=pain_points,
        maturity_scores=a.maturity_scores or {},
        recommendations=recs,
        government_support=govs,
        lead_score=a.lead_score,
        maturity_gap_explanation=(a.diagnosis.get("narrative_report") or {}).get("maturity_gap_explanation")
    )

    rules = load_supporting_rules().model_dump()
    metrics = lead_metrics_from_assessment(a, rules)
    lead_score_reasons = a.lead_score_reasons or metrics["lead_score_reasons"]
    sales_brief = normalize_sales_brief(
        a.sales_brief or {},
        a.company_profile,
        pain_points,
        lead_score_reasons,
        recs,
    )
    if not lead_score_reasons:
        lead_score_reasons = sales_brief.get("why_this_lead_is_hot") or []

    return LeadDetailResponse(
        assessment_id=a.assessment_id,
        lead_label=format_lead_label(a.company_profile, a.assessment_id),
        company_profile=a.company_profile,
        lead_score=a.lead_score,
        lead_score_reasons=lead_score_reasons,
        sales_brief=sales_brief,
        diagnosis_data=diag_resp,
        impact_simulation=a.impact_simulation or None
    )
