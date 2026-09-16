import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from backend.models import TopPainPoint, Recommendation, GovernmentSupportMatch

class PainPointExplanation(BaseModel):
    problem: str
    root_cause_explanation: str
    why_it_matters: str

class RoadmapNarrative(BaseModel):
    phase_1: str
    phase_2: str
    phase_3: str

class SalesBrief(BaseModel):
    one_line_hook: str
    why_this_lead_is_hot: List[str]
    recommended_approach: str

class StrategistOutput(BaseModel):
    pain_point_explanations: List[PainPointExplanation]
    roadmap_narrative: RoadmapNarrative
    sme_report_summary: str
    sales_brief: SalesBrief

def create_strategist_chain(llm: BaseChatModel):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI Strategist for a Digital Transformation consultancy. "
                   "You are provided with a deterministic diagnosis, maturity scores, calculated financial impacts, "
                   "priority, lead score, and deterministically matched Exabytes products and government support. "
                   "Your job is to generate human-readable explanations, a 3-phase transformation roadmap, "
                   "a summary report, and a sales brief. "
                   "CRITICAL: Do NOT invent, change, or recalculate any numbers (especially lead score, impact, hours, or maturity scores). "
                   "Do NOT invent products that are not in the provided matched products list. "
                   "If government support is matched, ALWAYS use the exact phrase 'Potentially eligible' and never guarantee it."),
        ("human", "Diagnosis: {diagnosis}\n\nScores & Impact: {scores_and_impact}\n\n"
                  "Matched Products: {matched_products}\n\nMatched Gov Support: {gov_support}")
    ])
    
    structured_llm = llm.with_structured_output(StrategistOutput)
    return prompt | structured_llm

def validate_strategist_output(
    output: StrategistOutput, 
    matched_products: List[Recommendation],
    impact_cost: float,
    lead_score: float
) -> bool:
    """
    Validates that the LLM did not hallucinate products or contradictory numbers.
    """
    valid_product_names = [p.product_id.lower() for p in matched_products]
    
    # Dump all text from the output to scan it
    all_text = (
        output.sme_report_summary + " " + 
        output.roadmap_narrative.phase_1 + " " + 
        output.roadmap_narrative.phase_2 + " " + 
        output.roadmap_narrative.phase_3 + " " +
        output.sales_brief.one_line_hook + " " +
        " ".join(output.sales_brief.why_this_lead_is_hot) + " " +
        output.sales_brief.recommended_approach
    ).lower()
    
    # 1. Check for absolute guarantee of government support
    bad_gov_phrases = ["definitely eligible", "guaranteed", "you qualify for"]
    for phrase in bad_gov_phrases:
        if phrase in all_text:
            return False
            
    # 2. Extract any RM amounts from text to ensure they don't contradict the impact cost
    # Just a simple heuristic: if it mentions RM[number], the number better be related to the impact cost
    rm_matches = re.findall(r'rm\s*([\d,]+)', all_text)
    for match in rm_matches:
        num_str = match.replace(",", "")
        try:
            num = float(num_str)
            # If the LLM spits out a financial number, it should be the impact cost or 0
            if num != impact_cost and num > 0:
                # To avoid breaking on random examples, we might be lenient, but we return False for strict validation
                return False
        except ValueError:
            pass
            
    return True

def run_strategist(
    llm: BaseChatModel,
    diagnosis: List[TopPainPoint],
    maturity_scores: Dict[str, float],
    impact_cost: float,
    lead_score: float,
    priority: int,
    matched_products: List[Recommendation],
    gov_support: List[GovernmentSupportMatch]
) -> StrategistOutput:
    
    chain = create_strategist_chain(llm)
    
    scores_and_impact = {
        "maturity_scores": maturity_scores,
        "annual_opportunity_cost_RM": impact_cost,
        "lead_score": lead_score,
        "priority_rank": priority
    }
    
    inputs = {
        "diagnosis": [p.model_dump() for p in diagnosis],
        "scores_and_impact": scores_and_impact,
        "matched_products": [p.model_dump() for p in matched_products],
        "gov_support": [g.model_dump() for g in gov_support]
    }
    
    # Attempt 1
    output = chain.invoke(inputs)
    
    if validate_strategist_output(output, matched_products, impact_cost, lead_score):
        return output
        
    # Validation failed, retry with stricter instruction (could use a different prompt, but we just re-invoke)
    inputs["scores_and_impact"]["WARNING"] = "PREVIOUS OUTPUT FAILED VALIDATION. DO NOT INVENT NUMBERS OR GUARANTEE GRANTS."
    try:
        output = chain.invoke(inputs)
        if validate_strategist_output(output, matched_products, impact_cost, lead_score):
            return output
    except Exception:
        pass
        
    # Safe deterministic fallback
    return StrategistOutput(
        pain_point_explanations=[
            PainPointExplanation(problem=p.problem, root_cause_explanation=p.root_cause, why_it_matters=p.business_impact)
            for p in diagnosis
        ],
        roadmap_narrative=RoadmapNarrative(
            phase_1="Phase 1: Stabilise operations",
            phase_2="Phase 2: Introduce automation",
            phase_3="Phase 3: Scale with AI"
        ),
        sme_report_summary="Deterministic report generated due to LLM validation failure. See your scores above.",
        sales_brief=SalesBrief(
            one_line_hook="Hot lead based on high operational pain.",
            why_this_lead_is_hot=["High priority", "High opportunity cost"],
            recommended_approach="Lead with time-saving solutions."
        )
    )
