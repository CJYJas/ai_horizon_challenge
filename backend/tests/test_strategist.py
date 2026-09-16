import pytest
from typing import Dict, Any
from backend.models import TopPainPoint, CompanyProfile, Recommendation, GovernmentSupportMatch
from backend.solution_matching.matcher import run_solution_matcher
from backend.ai_chains.strategist import (
    run_strategist, 
    StrategistOutput, 
    PainPointExplanation, 
    RoadmapNarrative, 
    SalesBrief,
    ProductRationale,
    SalesPlaybook,
    validate_strategist_output
)
from backend.ai_chains.analyst import run_analyst_loop, AnalystOutput, InformationGap

class MockAnalystChain:
    def invoke(self, inputs: Dict[str, Any]):
        return AnalystOutput(
            hypotheses=["Customer-order management bottleneck"],
            confidence="high",
            information_gap=InformationGap(
                exists=False,
                reason="Sufficient evidence.",
                follow_up_question=None
            )
        )

class MockStrategistChain:
    def invoke(self, inputs: Dict[str, Any]):
        return StrategistOutput(
            pain_point_explanations=[
                PainPointExplanation(
                    problem="Hard to keep track of customer orders",
                    root_cause_explanation="Fragmented WhatsApp communications.",
                    why_it_matters="Loss of RM 20,800/year" # Valid RM number based on scenario
                )
            ],
            roadmap_narrative=RoadmapNarrative(
                phase_1="Implement FreshDesk",
                phase_2="Automate with CRM",
                phase_3="Add AI"
            ),
            sme_report_summary="Potentially eligible for HRD Corp grants.",
            sales_brief=SalesBrief(
                one_line_hook="Hot lead",
                why_this_lead_is_hot=["High urgency"],
                recommended_approach="Sell CRM"
            ),
            product_rationales=[
                ProductRationale(
                    product_id=product["product_id"],
                    observed_evidence=["Answers"],
                    why_suitable="Matched to the observed workflow.",
                    relevant_capabilities=["Workflow support"],
                    implementation_suggestion="Start with one workflow.",
                    expected_outcome="Improve workflow visibility.",
                )
                for product in inputs["matched_products"]
            ],
            sales_playbook=SalesPlaybook(
                discovery_questions=["What is the current workflow?"],
                talk_track=["Connect the workflow to the solution."],
                next_actions=["Book a discovery call."],
            ),
        )

class MockBadStrategistChain:
    def invoke(self, inputs: Dict[str, Any]):
        return StrategistOutput(
            pain_point_explanations=[
                PainPointExplanation(
                    problem="Hard to keep track of customer orders",
                    root_cause_explanation="Fragmented WhatsApp communications.",
                    why_it_matters="Loss of RM 99,999/year" # INVALID RM number
                )
            ],
            roadmap_narrative=RoadmapNarrative(
                phase_1="Phase 1",
                phase_2="Phase 2",
                phase_3="Phase 3"
            ),
            sme_report_summary="You are definitely eligible for a RM500,000 grant.", # INVALID absolute claim
            sales_brief=SalesBrief(
                one_line_hook="Hot lead",
                why_this_lead_is_hot=["High urgency"],
                recommended_approach="Sell CRM"
            )
        )

def test_phase_5_abc_enterprise_pipeline(monkeypatch):
    """
    Tests the complete pipeline:
    Diagnosis -> Scoring (mocked/simulated) -> Matcher -> Strategist
    """
    profile = CompanyProfile(
        industry="Retail",
        employee_count=8,
        current_digital_tools=["whatsapp", "spreadsheet"],
        main_operational_problems=["Hard to keep track of customer orders"]
    )
    
    pain_points = [
        TopPainPoint(
            problem="Hard to keep track of customer orders",
            root_cause="Customer interactions fragmented across WhatsApp + spreadsheets + multiple staff",
            evidence=["Answers"],
            business_impact="~RM20,800/year labour opportunity",
            impact_estimate="20800",
            urgency="high",
            priority_rank=1
        )
    ]
    
    # 1. Solution Matcher
    matching_result = run_solution_matcher(pain_points, profile)
    
    recs = matching_result["recommendations"]
    gov = matching_result["government_support"]
    
    # Verify deterministic matcher results
    assert len(recs) > 0
    # The scenario has whatsapp/fragmented + CRM needs, should match Freshdesk, Freshchat or Lark
    matched_ids = [r.product_id for r in recs]
    assert any(p_id in ["freshdesk", "freshchat", "lark"] for p_id in matched_ids)
    
    # Verify gov support
    assert len(gov) > 0
    assert "Potentially eligible" in gov[0].eligibility_status
    
    # 2. Strategist Chain
    monkeypatch.setattr("backend.ai_chains.strategist.create_strategist_chain", lambda llm: MockStrategistChain())
    
    output = run_strategist(
        llm=None,
        diagnosis=pain_points,
        maturity_scores={"digital_presence": 2.0},
        impact_cost=20800.0,
        lead_score=92.0,
        priority=1,
        matched_products=recs,
        gov_support=gov
    )
    
    # Verify Strategist output
    assert output.roadmap_narrative.phase_1 == "Implement FreshDesk"
    assert "Potentially eligible" in output.sme_report_summary
    
def test_strategist_validation_failure_fallback(monkeypatch):
    """
    Tests that if the LLM hallucinates numbers or guaranteed grants, the validation catches it 
    and triggers the deterministic fallback.
    """
    pain_points = [
        TopPainPoint(
            problem="Test problem",
            root_cause="Test root cause",
            evidence=[],
            business_impact="Impact",
            impact_estimate="100",
            urgency="high",
            priority_rank=1
        )
    ]
    
    monkeypatch.setattr("backend.ai_chains.strategist.create_strategist_chain", lambda llm: MockBadStrategistChain())
    
    output = run_strategist(
        llm=None,
        diagnosis=pain_points,
        maturity_scores={"digital_presence": 2.0},
        impact_cost=20800.0, # Valid cost is 20800
        lead_score=92.0,
        priority=1,
        matched_products=[],
        gov_support=[]
    )
    
    # The MockBadStrategistChain mentions RM 99,999 and "definitely eligible", so validation should FAIL
    # It should fall back to the safe deterministic output
    assert "Test problem" in output.sme_report_summary
    assert "Test problem" in output.roadmap_narrative.phase_1
