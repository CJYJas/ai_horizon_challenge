import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
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
    sme_situation_summary: Optional[str] = None
    suggested_conversation_angle: Optional[str] = None


class ProductRationale(BaseModel):
    product_id: str
    observed_evidence: List[str] = Field(default_factory=list)
    why_suitable: str = ""
    relevant_capabilities: List[str] = Field(default_factory=list)
    implementation_suggestion: str = ""
    prerequisites: List[str] = Field(default_factory=list)
    expected_outcome: str = ""


class SalesPlaybook(BaseModel):
    situation_summary: str = ""
    discovery_questions: List[str] = Field(default_factory=list)
    talk_track: List[str] = Field(default_factory=list)
    likely_objections: List[str] = Field(default_factory=list)
    objection_responses: List[str] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)

class StrategistOutput(BaseModel):
    pain_point_explanations: List[PainPointExplanation]
    roadmap_narrative: RoadmapNarrative
    sme_report_summary: str
    sales_brief: SalesBrief
    product_rationales: List[ProductRationale] = Field(default_factory=list)
    sales_playbook: SalesPlaybook = Field(default_factory=SalesPlaybook)
    maturity_gap_explanation: Optional[str] = Field(default=None, description="A 1-2 sentence explanation of why the company scored lowest in their weakest digital maturity dimension, based on their current tools and diagnosis.")


def _invoke_chain(chain, inputs: Dict[str, Any]):
    """Support LangChain runnables and lightweight test doubles."""
    return chain(inputs) if callable(chain) else chain.invoke(inputs)

def create_strategist_chain(llm: BaseChatModel):
    parser = PydanticOutputParser(pydantic_object=StrategistOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI Strategist for a Digital Transformation consultancy. "
                   "You are provided with a deterministic diagnosis, maturity scores, calculated financial impacts, "
                   "priority, lead score, and deterministically matched Exabytes products and government support. "
                   "Your job is to generate human-readable explanations, a 3-phase transformation roadmap, "
                   "a summary report, and a sales brief. "
                   "CRITICAL: Do NOT invent, change, or recalculate any numbers (especially lead score, impact, hours, or maturity scores). "
                   "Do NOT invent products that are not in the provided matched products list. "
                   "CRITICAL REQUIREMENT: For EVERY SINGLE matched product in the input, you MUST include a corresponding detailed 'product_rationales' entry. "
                   "Provide extremely strong, detailed, and persuasive reasoning for why the product is suitable based on the exact assessment evidence. Include clear 'how to start' steps. "
                   "Also produce a practical and detailed sales playbook: discovery questions, talk track, likely objections with strong responses, and next actions. "
                   "You must also generate a 'maturity_gap_explanation' which is a 1-2 sentence explanation of why the company scored lowest in their weakest digital maturity dimension, based on their current tools. "
                   "If government support is matched, ALWAYS use the exact phrase 'Potentially eligible' and never guarantee it.\n"
                   "{format_instructions}"),
        ("human", "Diagnosis: {diagnosis}\n\nScores & Impact: {scores_and_impact}\n\n"
                  "Matched Products: {matched_products}\n\nVerified Product Context: {product_context}\n\nMatched Gov Support: {gov_support}")
    ])
    
    structured_llm = llm.with_structured_output(StrategistOutput)
    
    def run_chain(inputs):
        inputs["format_instructions"] = parser.get_format_instructions()
        try:
            return (prompt | structured_llm).invoke(inputs)
        except Exception:
            # Fallback for models that fail structured output
            raw_result = (prompt | llm).invoke(inputs)
            try:
                return parser.parse(raw_result.content)
            except Exception:
                # Regex fallback
                match = re.search(r'```json\n(.*?)\n```', raw_result.content, re.DOTALL)
                if match:
                    return StrategistOutput.model_validate_json(match.group(1))
                raise
                
    return run_chain

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

    rationale_ids = {item.product_id.lower() for item in output.product_rationales}
    if set(valid_product_names) != rationale_ids:
        return False
    if not output.sales_playbook.discovery_questions or not output.sales_playbook.talk_track or not output.sales_playbook.next_actions:
        return False
    
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
    gov_support: List[GovernmentSupportMatch],
    product_context: Optional[Dict[str, Dict[str, Any]]] = None,
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
        "product_context": product_context or {},
        "gov_support": [g.model_dump() for g in gov_support]
    }
    
    # Use the LLM whenever it returns a safe, structured answer. If a provider
    # is unavailable or an answer fails validation, continue with a contextual
    # narrative rather than returning a broken report or canned sales copy.
    try:
        output = _invoke_chain(chain, inputs)
        if validate_strategist_output(output, matched_products, impact_cost, lead_score):
            return output
        else:
            print("Validation failed on first attempt.")

        inputs["scores_and_impact"]["WARNING"] = (
            "PREVIOUS OUTPUT FAILED VALIDATION. DO NOT INVENT NUMBERS OR GUARANTEE GRANTS."
        )
        output = _invoke_chain(chain, inputs)
        if validate_strategist_output(output, matched_products, impact_cost, lead_score):
            return output
        else:
            print("Validation failed on second attempt.")
    except Exception as e:
        print("Exception in Strategist chain:", e)
        pass

    # Safe assessment-specific fallback. It uses diagnosis evidence and the
    # verified product catalog instead of a generic hardcoded sales story.
    primary_pain = diagnosis[0] if diagnosis else None
    primary_problem = primary_pain.problem if primary_pain else "the identified operational bottleneck"
    primary_cause = primary_pain.root_cause if primary_pain else "the current operating process"
    products = [product.product_id.upper() for product in matched_products]
    primary_product = products[0] if products else "the recommended Exabytes solution"
    secondary_product = products[1] if len(products) > 1 else primary_product
    lowest_dimension = min(maturity_scores, key=maturity_scores.get) if maturity_scores else "digital operations"
    readable_dimension = lowest_dimension.replace("_", " ")
    impact_note = f" The current annual opportunity cost is RM {impact_cost:,.0f}." if impact_cost else ""
    evidence = primary_pain.evidence if primary_pain else []
    rationales = []
    for recommendation in matched_products:
        context = (product_context or {}).get(recommendation.product_id, {})
        benefits = context.get("benefits") or [recommendation.expected_outcome]
        prerequisites = context.get("prerequisites") or []
        rationales.append(ProductRationale(
            product_id=recommendation.product_id,
            observed_evidence=evidence,
            why_suitable=(
                f"{recommendation.product_id.upper()} is matched to {recommendation.linked_pain_point} because "
                f"the assessment identifies {primary_cause}."
            ),
            relevant_capabilities=benefits,
            implementation_suggestion=(
                f"Start with the workflow causing {primary_problem}, assign one process owner, "
                "and review adoption after the first operating cycle."
            ),
            prerequisites=prerequisites,
            expected_outcome=recommendation.expected_outcome,
        ))

    return StrategistOutput(
        pain_point_explanations=[
            PainPointExplanation(problem=p.problem, root_cause_explanation=p.root_cause, why_it_matters=p.business_impact)
            for p in diagnosis
        ],
        roadmap_narrative=RoadmapNarrative(
            phase_1=f"Standardise the workflow behind {primary_problem} and remove friction from {primary_cause}.",
            phase_2=f"Deploy {primary_product} as the first focused improvement, with a process owner and adoption check-in.",
            phase_3=f"Use {secondary_product} to build on the improved {readable_dimension} capability as the business grows."
        ),
        sme_report_summary=(
            f"The assessment points to {primary_problem}, driven by {primary_cause}. "
            f"The recommended first move is {primary_product}, with extra attention on {readable_dimension}."
            f"{impact_note}"
        ),
        sales_brief=SalesBrief(
            one_line_hook=f"{primary_problem}: a focused {primary_product} conversation is timely.",
            why_this_lead_is_hot=[
                f"Confirmed operational bottleneck: {primary_problem}",
                f"Root cause is specific and actionable: {primary_cause}",
                f"Recommended solution is already matched to the diagnosis: {primary_product}",
            ],
            recommended_approach=(
                f"Start with how {primary_product} reduces the work around {primary_problem}; "
                "validate the team’s current workflow before discussing rollout."
            ),
            sme_situation_summary=(
                f"The business is experiencing {primary_problem}. The diagnosis links it to {primary_cause}."
            ),
            suggested_conversation_angle=(
                f"Ask the prospect to walk through the bottleneck, then show the smallest {primary_product} "
                "workflow that removes that friction."
            ),
        ),
        product_rationales=rationales,
        sales_playbook=SalesPlaybook(
            situation_summary=f"{primary_problem} is linked to {primary_cause}.",
            discovery_questions=[
                f"Can you walk me through where {primary_problem.lower()} happens today?",
                "Which team member owns the process when an exception occurs?",
                "What would a successful first month of improvement look like?",
            ],
            talk_track=[
                f"Reflect the evidence: {primary_problem} is creating avoidable friction.",
                f"Connect the cause to a focused {primary_product} workflow, rather than a disruptive replacement.",
                "Agree on one measurable workflow outcome before discussing a wider rollout.",
            ],
            likely_objections=["We are too busy to change our process.", "We need to see value before committing."],
            objection_responses=[
                "Start with one contained workflow and a named owner to minimise disruption.",
                "Use the agreed workflow outcome and current effort as the review point for the first phase.",
            ],
            next_actions=[
                "Book a workflow-discovery session with the process owner.",
                f"Demonstrate {primary_product} against the identified bottleneck.",
                "Confirm implementation prerequisites and a first-phase success measure.",
            ],
        ),
        maturity_gap_explanation=f"With the current tools, {readable_dimension} represents the largest gap and the most immediate opportunity for ROI."
    )
