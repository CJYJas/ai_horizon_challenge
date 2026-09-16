from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
import json
import re


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
        overlap = len(candidate & previous) / min(len(candidate), len(previous))
        if overlap >= 0.6:
            return True
    return False


def _invoke_chain(chain, inputs: Dict[str, Any]):
    """Support LangChain runnables and lightweight test doubles."""
    return chain(inputs) if callable(chain) else chain.invoke(inputs)

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
                   "if it has already been answered, use it rather than asking it again.\n{format_instructions}"),
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
                hypotheses=["Error during analysis"],
                confidence="low",
                information_gap=InformationGap(exists=False, reason=str(e), follow_up_question=None)
            )
            
        if not output.information_gap.exists or not output.information_gap.follow_up_question:
            # Stop the loop
            return output, answers

        if is_repeated_question(output.information_gap.follow_up_question, answers):
            # A repeated question cannot add information. Finish this turn with
            # the evidence already collected instead of trapping the user.
            output.information_gap = InformationGap(
                exists=False,
                reason="The proposed follow-up overlaps with information already provided.",
                follow_up_question=None,
            )
            return output, answers
            
        # Ask follow up
        if ask_user_func:
            question = output.information_gap.follow_up_question
            user_response = ask_user_func(question)
            answers.append({
                "question_id": f"q_{len(answers)+1}",
                "question_text": question,
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
            hypotheses=["Error during final analysis"],
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
        except Exception as e:
            # Fallback
            return [DiagnosticPoint(
                problem=hypotheses[0] if hypotheses else "Operational inefficiency",
                root_cause="Fragmented digital operations",
                evidence=["User assessment responses"],
                business_impact="Revenue and productivity leak"
            )]
