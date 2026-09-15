from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel

class InformationGap(BaseModel):
    exists: bool = Field(description="Whether a genuine information gap exists that changes the diagnosis")
    reason: str = Field(description="What is missing and why it matters")
    follow_up_question: Optional[str] = Field(None, description="Exactly one well-targeted follow-up question")

class AnalystOutput(BaseModel):
    hypotheses: List[str] = Field(description="Structured hypotheses about business problems")
    confidence: str = Field(description="Confidence level: low, medium, or high")
    information_gap: InformationGap

def create_analyst_chain(llm: BaseChatModel):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI Digital Transformation Consultant diagnosing SME business problems. "
                   "Based on the company profile and answers provided, form hypotheses about their operational bottlenecks. "
                   "If you need more information to make a confident diagnosis, identify the information gap and ask ONE targeted follow-up question. "
                   "Do not ask a checklist of questions."),
        ("human", "Company Profile: {company_profile}\n\nAnswers so far: {answers}")
    ])
    
    # Use structured output
    structured_llm = llm.with_structured_output(AnalystOutput)
    
    chain = prompt | structured_llm
    return chain

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
            output = chain.invoke({
                "company_profile": company_profile,
                "answers": answers
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
            # Loop breaks if there's no way to ask the user
            break
            
    # If the max question cap is reached, enforce exists = False
    try:
        output = chain.invoke({
            "company_profile": company_profile,
            "answers": answers
        })
        output.information_gap.exists = False
    except Exception as e:
        output = AnalystOutput(
            hypotheses=["Error during final analysis"],
            confidence="low",
            information_gap=InformationGap(exists=False, reason=str(e), follow_up_question=None)
        )

    return output, answers
