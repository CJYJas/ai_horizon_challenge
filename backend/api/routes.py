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
    ReportResponse, LeadCardResponse, LeadDetailResponse
)
from backend.models import SMEAssessment, TopPainPoint, Recommendation, GovernmentSupportMatch, CompanyProfile
from backend.ai_chains.analyst import run_analyst_loop
from backend.ai_chains.strategist import run_strategist
from backend.scoring.engine import (
    calculate_maturity_scores, calculate_weighted_maturity,
    calculate_impact, classify_impact, classify_urgency,
    calculate_priority, calculate_lead_score, generate_lead_score_reasons
)
from backend.solution_matching.matcher import run_solution_matcher
from backend.data_loaders import load_supporting_rules

router = APIRouter()

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
    return CreateAssessmentResponse(assessment_id=assessment.assessment_id, status="Created")

@router.post("/assessments/{id}/answers", response_model=AnswerResponse)
def add_answer(id: str, req: AnswerRequest, db: Session = Depends(get_session), llm = Depends(get_llm)):
    assessment = db.get(SMEAssessment, id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    # Append answer
    answers = assessment.answers or []
    answers.append({
        "question_id": f"q_{len(answers)+1}",
        "question_text": "Follow up", # In a real app we'd track the question text asked
        "answer": req.answer,
        "asked_reason": "Dynamic"
    })
    
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
            reason=output.information_gap.reason
        )
    else:
        # Save hypotheses as basic diagnosis text
        assessment.diagnosis = {"hypotheses": output.hypotheses}
        db.add(assessment)
        db.commit()
        return AnswerResponse(is_complete=True)

@router.get("/assessments/{id}/diagnosis", response_model=DiagnosisResponse)
def get_diagnosis(id: str, db: Session = Depends(get_session)):
    assessment = db.get(SMEAssessment, id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    rules = load_supporting_rules().model_dump()
    
    # Generate mock pain points from hypotheses if real ones don't exist yet
    # In a full flow, a dedicated Diagnosis Chain would run here
    hypotheses = assessment.diagnosis.get("hypotheses", ["General operational bottleneck"])
    problem_str = hypotheses[0] if hypotheses else "Operational inefficiency"
    
    # Determine deterministic scores based on current profile and answers
    mat_scores = calculate_maturity_scores(assessment.company_profile, rules)
    overall_maturity = calculate_weighted_maturity(mat_scores, rules)
    
    # Default impact values based on demo scenario if user hasn't set them via simulation endpoint
    sim = assessment.impact_simulation or {}
    hrs_per_week = sim.get("input_hours_per_week", 20.0)
    hr_rate = sim.get("hourly_rate_assumption", 25.0)
    impact_cost = calculate_impact(hrs_per_week, hr_rate, rules)
    
    urgency = classify_urgency(["currently_losing_customers"] if "whatsapp" in assessment.company_profile.get("current_digital_tools", []) else [], rules)
    impact_level = classify_impact(impact_cost, rules)
    priority = calculate_priority(impact_level, urgency, rules)
    lead_score = calculate_lead_score(impact_cost, urgency, overall_maturity, rules)
    
    pain_points = [
        TopPainPoint(
            problem=problem_str,
            root_cause="Fragmented digital operations",
            evidence=["See answers"],
            business_impact=f"~RM{impact_cost}/year",
            impact_estimate=str(impact_cost),
            urgency=urgency,
            priority_rank=priority
        )
    ]
    
    # Match solutions
    # Need to cast profile dict to CompanyProfile schema
    profile_model = CompanyProfile(**assessment.company_profile)
    matches = run_solution_matcher(pain_points, profile_model)
    
    # Persist the generated data
    assessment.maturity_scores = mat_scores
    assessment.recommendations = [r.model_dump() for r in matches["recommendations"]]
    assessment.government_support = [g.model_dump() for g in matches["government_support"]]
    assessment.lead_score = lead_score
    db.add(assessment)
    db.commit()
    
    return DiagnosisResponse(
        top_pain_points=pain_points,
        maturity_scores=mat_scores,
        recommendations=matches["recommendations"],
        government_support=matches["government_support"],
        lead_score=lead_score
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
        
    # Recreate the models for strategist
    pain_points = [
        TopPainPoint(
            problem=assessment.diagnosis.get("hypotheses", ["Operational bottleneck"])[0],
            root_cause="Fragmented tools",
            evidence=[],
            business_impact="High",
            impact_estimate="20800",
            urgency="high",
            priority_rank=1
        )
    ]
    recs = [Recommendation(**r) for r in assessment.recommendations]
    govs = [GovernmentSupportMatch(**g) for g in assessment.government_support]
    
    sim = assessment.impact_simulation or {}
    impact_cost = sim.get("annual_opportunity_cost", 20800.0)
    
    try:
        report = run_strategist(
            llm=llm,
            diagnosis=pain_points,
            maturity_scores=assessment.maturity_scores,
            impact_cost=impact_cost,
            lead_score=assessment.lead_score,
            priority=1,
            matched_products=recs,
            gov_support=govs
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Report generation failed")
        
    # Save the sales brief reasons and the full brief to DB
    assessment.lead_score_reasons = report.sales_brief.why_this_lead_is_hot
    assessment.sales_brief = report.sales_brief.model_dump()
    db.add(assessment)
    db.commit()
    
    # Construct complete report response
    diag_resp = DiagnosisResponse(
        top_pain_points=pain_points,
        maturity_scores=assessment.maturity_scores,
        recommendations=recs,
        government_support=govs,
        lead_score=assessment.lead_score
    )
    
    return ReportResponse(
        report=report,
        company_profile=assessment.company_profile,
        diagnosis_data=diag_resp,
        impact_simulation=assessment.impact_simulation
    )

@router.get("/leads", response_model=List[LeadCardResponse])
def get_leads(db: Session = Depends(get_session)):
    assessments = db.exec(select(SMEAssessment).order_by(SMEAssessment.lead_score.desc())).all()
    
    leads = []
    for a in assessments:
        problem = None
        priority = 0
        rec_trans = None
        
        # Use first recommendation's linked product or transformation
        if a.recommendations and len(a.recommendations) > 0:
            rec_trans = a.recommendations[0].get("product_id", "Digital Solution")
            
        # Get problem and priority from diagnosis top pain points if available
        # Wait, pain_points might not be persisted directly in assessment.diagnosis for older records.
        # But for new ones we didn't persist pain_points into diagnosis dict properly, we generated it on the fly.
        # Let's extract from hypotheses if pain_points missing
        hypotheses = a.diagnosis.get("hypotheses", ["Operational bottleneck"]) if a.diagnosis else ["Operational bottleneck"]
        problem = hypotheses[0] if hypotheses else None
        priority = a.diagnosis.get("priority", 3) if a.diagnosis else 3
        
        # Calculate overall maturity
        scores = a.maturity_scores or {}
        overall = sum(scores.values()) / len(scores) if scores else 0.0

        leads.append(LeadCardResponse(
            assessment_id=a.assessment_id,
            company_name=a.company_profile.get("company_name", "ABC Enterprise"),
            company_industry=a.company_profile.get("industry", "Unknown"),
            employee_count=a.company_profile.get("employee_count", 0),
            overall_maturity=overall,
            lead_score=a.lead_score,
            priority=priority,
            top_pain_point_problem=problem,
            recommended_transformation=rec_trans,
            created_at=a.created_at
        ))
    return leads

@router.get("/leads/{id}", response_model=LeadDetailResponse)
def get_lead_detail(id: str, db: Session = Depends(get_session)):
    a = db.get(SMEAssessment, id)
    if not a:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # Reconstruct DiagnosisResponse
    hypotheses = a.diagnosis.get("hypotheses", ["Operational bottleneck"]) if a.diagnosis else ["Operational bottleneck"]
    
    # We must fake TopPainPoint based on existing data to not break schema since we didn't persist it fully
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
        lead_score=a.lead_score
    )
        
    return LeadDetailResponse(
        assessment_id=a.assessment_id,
        company_profile=a.company_profile,
        lead_score=a.lead_score,
        lead_score_reasons=a.lead_score_reasons,
        sales_brief=a.sales_brief,
        diagnosis_data=diag_resp,
        impact_simulation=a.impact_simulation
    )
