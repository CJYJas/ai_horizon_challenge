import pytest
from typing import Dict, Any, List
from backend.ai_chains.analyst import (
    run_analyst_loop, 
    AnalystOutput, 
    InformationGap,
    create_analyst_chain
)

class MockChain:
    def __init__(self, responses: List[AnalystOutput]):
        self.responses = responses
        self.call_count = 0
        
    def invoke(self, inputs: Dict[str, Any]):
        if self.call_count < len(self.responses):
            resp = self.responses[self.call_count]
            self.call_count += 1
            return resp
        # Default fallback
        return AnalystOutput(
            hypotheses=["Final diagnosis"],
            confidence="high",
            information_gap=InformationGap(exists=False, reason="Done", follow_up_question=None)
        )

def test_abc_enterprise_scenario(monkeypatch):
    # Setup mock responses matching the scenario
    mock_responses = [
        # Loop 1
        AnalystOutput(
            hypotheses=["Customer-order management bottleneck"],
            confidence="low",
            information_gap=InformationGap(
                exists=True,
                reason="Need to quantify manual effort.",
                follow_up_question="How many hours per week does your team spend handling customer enquiries and orders?"
            )
        ),
        # Loop 2
        AnalystOutput(
            hypotheses=["Customer-order management bottleneck", "Time lost to manual work"],
            confidence="medium",
            information_gap=InformationGap(
                exists=True,
                reason="Need to determine if process fragmentation leads to lost revenue.",
                follow_up_question="Do you lose enquiries/orders because multiple staff members handle WhatsApp separately?"
            )
        ),
        # Loop 3
        AnalystOutput(
            hypotheses=["Customer-order management bottleneck", "Fragmented comms causing lost revenue"],
            confidence="high",
            information_gap=InformationGap(
                exists=False,
                reason="Sufficient evidence collected.",
                follow_up_question=None
            )
        )
    ]
    
    mock_chain = MockChain(mock_responses)
    
    # Patch create_analyst_chain to return our MockChain
    monkeypatch.setattr("backend.ai_chains.analyst.create_analyst_chain", lambda llm: mock_chain)
    
    # User's predefined answers
    user_answers = [
        "20 hrs/week",
        "Yes"
    ]
    
    def mock_ask_user(question: str) -> str:
        # Pop the first answer from the list
        return user_answers.pop(0)

    company_profile = {
        "industry": "Retail",
        "employee_count": 8,
        "current_digital_tools": ["whatsapp", "spreadsheet"],
        "main_operational_problems": ["Hard to keep track of customer orders"]
    }
    
    initial_answers = []
    
    # Run the loop
    # We pass None for llm since it's mocked
    final_output, final_answers = run_analyst_loop(
        llm=None,
        company_profile=company_profile,
        initial_answers=initial_answers,
        max_questions=10,
        ask_user_func=mock_ask_user
    )
    
    # Assertions
    # 2 follow up questions should have been asked and answered
    assert len(final_answers) == 2
    assert final_answers[0]["question_text"] == "How many hours per week does your team spend handling customer enquiries and orders?"
    assert final_answers[0]["answer"] == "20 hrs/week"
    assert final_answers[0]["asked_reason"] == "Need to quantify manual effort."
    
    assert final_answers[1]["question_text"] == "Do you lose enquiries/orders because multiple staff members handle WhatsApp separately?"
    assert final_answers[1]["answer"] == "Yes"
    
    # The final output should have no gap
    assert final_output.information_gap.exists == False
    assert final_output.confidence == "high"
    
def test_fallback_on_exception(monkeypatch):
    class ErrorChain:
        def invoke(self, inputs):
            raise ValueError("Schema validation failed")
            
    monkeypatch.setattr("backend.ai_chains.analyst.create_analyst_chain", lambda llm: ErrorChain())
    
    final_output, final_answers = run_analyst_loop(
        llm=None,
        company_profile={},
        initial_answers=[],
        max_questions=10
    )
    
    assert final_output.information_gap.exists == False
    assert "Error during analysis" in final_output.hypotheses
    assert len(final_answers) == 0

def test_max_question_cap(monkeypatch):
    # Setup chain that always wants to ask a question
    class InfiniteGapChain:
        def invoke(self, inputs):
            return AnalystOutput(
                hypotheses=["Still uncertain"],
                confidence="low",
                information_gap=InformationGap(
                    exists=True,
                    reason="I need more info.",
                    follow_up_question="More questions?"
                )
            )
            
    monkeypatch.setattr("backend.ai_chains.analyst.create_analyst_chain", lambda llm: InfiniteGapChain())
    
    def mock_ask_user(question: str) -> str:
        return "Always an answer"
        
    final_output, final_answers = run_analyst_loop(
        llm=None,
        company_profile={},
        initial_answers=[],
        max_questions=3,
        ask_user_func=mock_ask_user
    )
    
    assert len(final_answers) == 3
    assert final_output.information_gap.exists == False
