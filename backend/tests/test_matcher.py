import pytest
from backend.models import TopPainPoint, CompanyProfile
from backend.solution_matching.matcher import run_solution_matcher

def test_abc_enterprise_demo_scenario():
    """
    Test the matcher using the ABC Enterprise demo scenario:
    - retail, 8 employees
    - WhatsApp + spreadsheets, manual enquiries
    """
    profile = CompanyProfile(
        name="ABC Enterprise",
        industry="Retail",
        employee_count=8,
        annual_revenue=150000.0,
        current_digital_tools=["WhatsApp", "Spreadsheets"],
        main_operational_problems=["Customer enquiries are difficult to manage"]
    )
    
    pain_points = [
        TopPainPoint(
            problem="Fragmented customer management and manual enquiries",
            evidence=["WhatsApp used for customer conversations", "Customer data in spreadsheets", "Manual customer follow-up"],
            root_cause="No centralized CRM system",
            why_it_matters="Leads are difficult to track and manual reporting wastes time.",
            root_cause_explanation="Data is scattered across manual tools.",
            business_impact_score=8,
            business_impact="High",
            impact_estimate="High",
            urgency="High",
            priority_rank=1
        )
    ]
    
    result = run_solution_matcher(pain_points, profile)
    
    recommendations = result.get("recommendations", [])
    gov_matches = result.get("government_support", [])
    
    assert len(recommendations) > 0, "Should have recommended at least one solution."
    
    # Check that freshsales or freshchat is recommended based on our overlap logic
    best_rec = recommendations[0]
    assert best_rec.product_id in ["freshsales", "freshchat", "freshdesk", "lark"]
    assert best_rec.explanation is not None
    assert len(best_rec.explanation.evidence) > 0
    assert best_rec.explanation.problem == pain_points[0].problem
    
    # Check government support condition splitting
    assert len(gov_matches) > 0
    for gov in gov_matches:
        assert gov.eligibility_status == "Potentially eligible"
        # Since ABC Enterprise is 8 employees, SME condition should be matched if present
        # And since they are "registered" or "SSM" (if any such conditions exist), they might be matched too.
        # But we mostly check that pending_conditions and matched_conditions exist.
        assert isinstance(gov.matched_conditions, list)
        assert isinstance(gov.pending_conditions, list)
