import pytest
from backend.scoring.engine import (
    calculate_maturity_scores,
    calculate_weighted_maturity,
    calculate_impact,
    classify_impact,
    classify_urgency,
    calculate_priority,
    calculate_lead_score,
    generate_lead_score_reasons
)
from backend.data_loaders import load_supporting_rules

@pytest.fixture
def rules():
    return load_supporting_rules().model_dump()

def test_calculate_maturity_scores(rules):
    profile = {"current_digital_tools": ["whatsapp", "spreadsheet"]}
    scores = calculate_maturity_scores(profile, rules)
    assert scores["digital_presence"] == 2.0
    assert scores["productivity"] == 2.0
    assert scores["customer_management"] == 2.0
    
def test_calculate_weighted_maturity(rules):
    scores = {
        "digital_presence": 2.0,
        "productivity": 2.0,
        "customer_management": 1.0,
        "data_security": 2.0,
        "ai_readiness": 1.0
    }
    # Using weights from default rules: 1, 1, 1.2, 1, 0.8
    # Total weight = 5.0
    # Expected total = 2 + 2 + 1.2 + 2 + 0.8 = 8.0
    # Expected weighted = 8.0 / 5.0 = 1.6
    weighted = calculate_weighted_maturity(scores, rules)
    assert weighted == 1.6

def test_calculate_impact(rules):
    # 20 hours * 52 weeks * 25 rate = 26000
    impact = calculate_impact(20, 25.0, rules)
    assert impact == 26000.0

def test_classify_impact(rules):
    assert classify_impact(0, rules) == "low"
    assert classify_impact(10000, rules) == "medium"
    assert classify_impact(26000, rules) == "high"

def test_classify_urgency(rules):
    assert classify_urgency(["minor_inconvenience"], rules) == "low"
    assert classify_urgency(["recurring_operational_problem"], rules) == "medium"
    assert classify_urgency(["currently_losing_customers", "minor_inconvenience"], rules) == "high"
    assert classify_urgency(["unknown_signal"], rules) == "low"

def test_calculate_priority(rules):
    assert calculate_priority("high", "high", rules) == 1
    assert calculate_priority("high", "medium", rules) == 2
    assert calculate_priority("low", "low", rules) == 5
    assert calculate_priority("medium", "high", rules) == 2

def test_calculate_lead_score(rules):
    # impact_cost=26000 (norm=75), urgency="high" (norm=100), maturity=1.6 (gap_norm=68)
    # weights: impact=0.5, urgency=0.3, gap=0.2
    # expected: (0.5 * 75) + (0.3 * 100) + (0.2 * 68) = 37.5 + 30 + 13.6 = 81.1
    score = calculate_lead_score(26000, "high", 1.6, rules)
    assert score == 81.1
    
    # Lowest
    score_low = calculate_lead_score(0, "low", 5.0, rules)
    # impact_norm=0, urgency_norm=33, gap_norm=0
    # expected: (0.3 * 33) = 9.9
    assert score_low == 9.9

def test_generate_lead_score_reasons(rules):
    reasons = generate_lead_score_reasons(26000, "high", 1.6, rules)
    assert "High operational impact" in reasons
    assert "High urgency" in reasons
    assert "Large digitalisation gap" in reasons
    assert "Significant estimated opportunity cost" in reasons
