from typing import List, Dict, Any, Optional
from langchain_core.language_models.chat_models import BaseChatModel

from backend.models import SMEAssessment, TopPainPoint, Recommendation, GovernmentSupportMatch, CompanyProfile
from backend.ai_chains.analyst import run_diagnosis_chain
from backend.ai_chains.strategist import run_strategist, StrategistOutput
from backend.scoring.engine import (
    calculate_maturity_scores, calculate_weighted_maturity,
    calculate_impact, classify_impact, classify_urgency, derive_urgency_signals,
    calculate_priority, calculate_lead_score, generate_lead_score_reasons
)
from backend.solution_matching.matcher import run_solution_matcher
from backend.data_loaders import load_supporting_rules, load_exabytes_products
from backend.api.lead_helpers import normalize_sales_brief


def _product_context(recommendations: List[Recommendation]) -> dict:
    catalog = {product.product_id: product for product in load_exabytes_products()}
    context = {}
    for recommendation in recommendations:
        product = catalog.get(recommendation.product_id)
        if product:
            context[product.product_id] = {
                "name": product.name,
                "benefits": product.benefits,
                "prerequisites": product.prerequisites,
                "category": product.category,
                "source_url": product.source_url,
            }
    return context


def lead_metrics_from_assessment(assessment: SMEAssessment, rules: dict) -> dict:
    sim = assessment.impact_simulation or {}
    hrs_per_week = sim.get("input_hours_per_week")
    hr_rate = sim.get("hourly_rate_assumption")
    impact_cost = calculate_impact(hrs_per_week, hr_rate, rules)

    mat_scores = assessment.maturity_scores or calculate_maturity_scores(assessment.company_profile, rules)
    overall_maturity = calculate_weighted_maturity(mat_scores, rules)

    urgency = classify_urgency(
        derive_urgency_signals(assessment.company_profile, assessment.answers or [], rules),
        rules,
    )
    impact_level = classify_impact(impact_cost, rules)
    priority = calculate_priority(impact_level, urgency, rules)
    lead_score = calculate_lead_score(impact_cost, urgency, overall_maturity, rules)
    reasons = generate_lead_score_reasons(impact_cost, urgency, overall_maturity, rules)

    return {
        "mat_scores": mat_scores,
        "overall_maturity": overall_maturity,
        "impact_cost": impact_cost,
        "urgency": urgency,
        "impact_level": impact_level,
        "priority": priority,
        "lead_score": lead_score,
        "lead_score_reasons": reasons,
    }


def generate_diagnosis(assessment: SMEAssessment, llm: BaseChatModel) -> Dict[str, Any]:
    """
    Core business logic for transforming answers into a diagnosis,
    scoring the SME, and matching solutions. Returns updated fields for DB persistence.
    """
    rules = load_supporting_rules().model_dump()
    hypotheses = (assessment.diagnosis or {}).get("hypotheses", ["General operational bottleneck"])
    
    # Run Diagnosis Chain
    diag_pts = run_diagnosis_chain(llm, assessment.company_profile, assessment.answers, hypotheses)
    
    metrics = lead_metrics_from_assessment(assessment, rules)
    
    pain_points = []
    for rank, pt in enumerate(diag_pts, start=1):
        pain_points.append(
            TopPainPoint(
                problem=pt.problem,
                root_cause=pt.root_cause,
                evidence=pt.evidence,
                business_impact=pt.business_impact,
                impact_estimate=str(metrics["impact_cost"]),
                urgency=metrics["urgency"],
                priority_rank=rank,
            )
        )
    
    profile_model = CompanyProfile(**assessment.company_profile)
    matches = run_solution_matcher(pain_points, profile_model)
    
    # Return structured dict of fields to update
    return {
        "pain_points": [p.model_dump() for p in pain_points],
        "maturity_scores": metrics["mat_scores"],
        "recommendations": [r.model_dump() for r in matches["recommendations"]],
        "government_support": [g.model_dump() for g in matches["government_support"]],
        "lead_score": metrics["lead_score"],
        "lead_score_reasons": metrics["lead_score_reasons"],
        "overall_priority": metrics["priority"]
    }


def generate_report(assessment: SMEAssessment, llm: BaseChatModel) -> StrategistOutput:
    """
    Core business logic for generating the LLM Strategist report.
    """
    stored_pain_points = assessment.diagnosis.get("pain_points", [])
    if stored_pain_points:
        pain_points = [TopPainPoint(**p) for p in stored_pain_points]
    else:
        # Fallback if somehow missing
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
    
    report = run_strategist(
        llm=llm,
        diagnosis=pain_points,
        maturity_scores=assessment.maturity_scores,
        impact_cost=impact_cost,
        lead_score=assessment.lead_score,
        priority=assessment.diagnosis.get("overall_priority", 1) if assessment.diagnosis else 1,
        matched_products=recs,
        gov_support=govs,
        product_context=_product_context(recs),
    )
    return report
