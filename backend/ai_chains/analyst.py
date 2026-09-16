from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
import json
import re


AUTHORITATIVE_PROFILE_TERMS = {
    "industry", "business sector", "sector", "employee", "employees", "staff", "worker", "workers",
    "people", "headcount", "size", "large",
    "company name", "business name",
    "email", "phone", "telephone", "contact number"
}
INTERVIEW_AGENDA = [
    ("tools_workflow", "Which tools, apps, or manual steps do you currently use to run this workflow?"),
    ("workload", "About how often does this workflow happen, and how much team time does it take in a typical week?"),
    ("outcome", "What would you most like to improve first: speed, fewer errors, customer response, or visibility?"),
]


def _question_terms(question: str) -> set[str]:
    """Normalise a question enough to catch reworded repeats."""
    stop_words = {"a", "an", "and", "are", "can", "could", "do", "does", "for", "how", "i", "if", "in", "is", "it", "many", "of", "or", "the", "to", "we", "what", "when", "which", "with", "would", "you", "your"}
    return {
        word for word in re.findall(r"[a-z0-9]+", (question or "").lower())
        if word not in stop_words and len(word) > 2
    }


def is_repeated_question(question: str, answers: List[Dict[str, Any]]) -> bool:
    """Return True for an exact or substantially overlapping previous prompt."""
    candidate = _question_terms(question)
    if not candidate:
        return False
    for item in answers:
        previous = _question_terms(str(item.get("question_text", "")))
        if not previous:
            continue
        # Use intersection size relative to minimum length to detect rewording
        overlap = len(candidate & previous) / max(min(len(candidate), len(previous)), 1)
        if overlap >= 0.5:
            return True
    return False


def classify_question_topic(question: str) -> str:
    terms = _question_terms(question)
    if terms & {"tool", "tools", "app", "apps", "system", "systems", "workflow", "process", "manual"}:
        return "tools_workflow"
    if terms & {"hour", "hours", "time", "often", "week", "volume"}:
        return "workload"
    if terms & {"improve", "goal", "outcome", "success", "priority", "want"}:
        return "outcome"
    return "adaptive"


def is_profile_question(question: str) -> bool:
    normalized = (question or "").lower()
    return any(term in normalized for term in AUTHORITATIVE_PROFILE_TERMS)


def next_safe_question(question: str, answers: List[Dict[str, Any]]) -> tuple[Optional[str], Optional[str]]:
    """Keep the interview on operational gaps and never repeat a topic."""
    asked_topics = {item.get("question_topic") or classify_question_topic(item.get("question_text", "")) for item in answers}
    candidate_topic = classify_question_topic(question)
    if question and not is_profile_question(question) and not is_repeated_question(question, answers) and candidate_topic not in asked_topics:
        return question, candidate_topic
    for topic, fallback in INTERVIEW_AGENDA:
        if topic not in asked_topics:
            return fallback, topic
    return None, None


def _invoke_chain(chain, inputs: Dict[str, Any]):
    """Support LangChain runnables and lightweight test doubles."""
    return chain(inputs) if callable(chain) else chain.invoke(inputs)


def _answer_texts(answers: List[Dict[str, Any]]) -> List[str]:
    return [str(item.get("answer", "")).strip() for item in answers if str(item.get("answer", "")).strip()]


def _fallback_hypothesis(company_profile: Dict[str, Any], answers: List[Dict[str, Any]]) -> str:
    stated_problem = (company_profile.get("main_operational_problems") or [None])[0]
    if stated_problem:
        return str(stated_problem)
    response = next(iter(_answer_texts(answers)), "")
    return f"Operational bottleneck described as: {response[:180]}" if response else "Error during analysis"

class InformationGap(BaseModel):
    exists: bool = Field(description="Whether a genuine information gap exists that changes the diagnosis")
    reason: str = Field(description="What is missing and why it matters")
    follow_up_question: Optional[str] = Field(None, description="Exactly one well-targeted follow-up question")

class AnalystOutput(BaseModel):
    hypotheses: List[str] = Field(description="Structured hypotheses about business problems")
    confidence: str = Field(description="Confidence level: low, medium, or high")
    information_gap: InformationGap

def create_analyst_chain(llm: BaseChatModel):
    parser = PydanticOutputParser(pydantic_object=AnalystOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI Digital Transformation Consultant diagnosing SME business problems. "
                   "Based on the company profile and answers provided, form hypotheses about their operational bottlenecks. "
                   "If you need more information to make a confident diagnosis, identify the information gap and ask ONE targeted follow-up question. "
                   "Do not ask a checklist of questions. Never repeat or substantially rephrase a question in the Answers so far; "
                   "if it has already been answered, use it rather than asking it again. Company name, industry, employee count, "
                   "email and phone are authoritative profile fields: never ask for them. Ask only about tools/workflow, workload, or desired outcome.\n{format_instructions}"),
        ("human", "Company Profile: {company_profile}\n\nAnswers so far: {answers}")
    ])
    
    # Try structured output first, but provide format_instructions for fallback parser
    structured_llm = llm.with_structured_output(AnalystOutput)
    
    def run_chain(inputs):
        try:
            return (prompt | structured_llm).invoke(inputs)
        except Exception:
            # Fallback for models that fail structured output
            raw_result = (prompt | llm).invoke(inputs)
            try:
                # Try standard parsing
                return parser.parse(raw_result.content)
            except Exception:
                # Regex fallback to extract JSON block
                match = re.search(r'```json\n(.*?)\n```', raw_result.content, re.DOTALL)
                if match:
                    return AnalystOutput.model_validate_json(match.group(1))
                raise
                
    return run_chain

def run_analyst_loop(
    llm: BaseChatModel, 
    company_profile: Dict[str, Any], 
    initial_answers: List[Dict[str, Any]], 
    max_questions: int = 10,
    ask_user_func=None
) -> Tuple[AnalystOutput, List[Dict[str, Any]]]:
    """
    Runs the adaptive assessment loop.
    Returns the final AnalystOutput and the complete list of answers.
    """
    answers = list(initial_answers)
    chain = create_analyst_chain(llm)
    
    while len(answers) < max_questions:
        try:
            output = _invoke_chain(chain, {
                "company_profile": company_profile,
                "answers": answers,
                "format_instructions": PydanticOutputParser(pydantic_object=AnalystOutput).get_format_instructions()
            })
        except Exception as e:
            # Fallback on schema validation failure or LLM error
            output = AnalystOutput(
                hypotheses=[_fallback_hypothesis(company_profile, answers)],
                confidence="low",
                information_gap=InformationGap(exists=False, reason=str(e), follow_up_question=None)
            )
            
        if not output.information_gap.exists or not output.information_gap.follow_up_question:
            # Stop the loop
            return output, answers

        safe_question, safe_topic = next_safe_question(output.information_gap.follow_up_question, answers)
        if not safe_question:
            output.information_gap = InformationGap(exists=False, reason="The interview agenda is complete.", follow_up_question=None)
            return output, answers
        output.information_gap.follow_up_question = safe_question
            
        # Ask follow up
        if ask_user_func:
            question = output.information_gap.follow_up_question
            user_response = ask_user_func(question)
            answers.append({
                "question_id": f"q_{len(answers)+1}",
                "question_text": question,
                "question_topic": safe_topic,
                "answer": user_response,
                "asked_reason": output.information_gap.reason
            })
        else:
            # The web client asks one question per request. Returning this
            # output (rather than invoking the LLM a second time) makes the
            # next prompt stable and prevents accidental repeat questions.
            return output, answers
            
    # If the max question cap is reached, enforce exists = False
    try:
        output = _invoke_chain(chain, {
            "company_profile": company_profile,
            "answers": answers,
            "format_instructions": PydanticOutputParser(pydantic_object=AnalystOutput).get_format_instructions()
        })
        output.information_gap.exists = False
    except Exception as e:
        output = AnalystOutput(
            hypotheses=[_fallback_hypothesis(company_profile, answers)],
            confidence="low",
            information_gap=InformationGap(exists=False, reason=str(e), follow_up_question=None)
        )

    return output, answers

class DiagnosticPoint(BaseModel):
    problem: str = Field(description="Clear operational problem")
    root_cause: str = Field(description="Root cause of the problem")
    evidence: List[str] = Field(description="Direct quotes or evidence from answers")
    business_impact: str = Field(description="Qualitative business impact")

class DiagnosisSynthesis(BaseModel):
    pain_points: List[DiagnosticPoint] = Field(description="Synthesized pain points")

def run_diagnosis_chain(llm: BaseChatModel, company_profile: Dict[str, Any], answers: List[Dict[str, Any]], hypotheses: List[str]) -> List[DiagnosticPoint]:
    parser = PydanticOutputParser(pydantic_object=DiagnosisSynthesis)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI Digital Transformation Consultant. Synthesize the collected hypotheses and answers into 1 or 2 high-impact Diagnostic Points. Ensure the evidence quotes the user's answers.\n{format_instructions}"),
        ("human", "Profile: {company_profile}\nAnswers: {answers}\nHypotheses: {hypotheses}")
    ])
    structured_llm = llm.with_structured_output(DiagnosisSynthesis)
    
    inputs = {
        "company_profile": company_profile,
        "answers": answers,
        "hypotheses": hypotheses,
        "format_instructions": parser.get_format_instructions()
    }
    
    try:
        res = (prompt | structured_llm).invoke(inputs)
        return res.pain_points
    except Exception:
        try:
            raw = (prompt | llm).invoke(inputs)
            res = parser.parse(raw.content)
            return res.pain_points
        except Exception:
            evidence = _answer_texts(answers) or [str(item) for item in (company_profile.get("main_operational_problems") or [])]
            first_evidence = evidence[0] if evidence else "the current workflow"
            return [DiagnosticPoint(
                problem=hypotheses[0] if hypotheses else f"Operational bottleneck in {company_profile.get('industry', 'the business')}",
                root_cause=f"Assessment evidence points to a workflow gap: {first_evidence[:220]}",
                evidence=evidence[:3] or ["No operational detail was supplied."],
                business_impact="The described manual workflow can create delays, errors, and reduced visibility."
            )]
