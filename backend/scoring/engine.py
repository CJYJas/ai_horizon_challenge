import math
from typing import Dict, Any, List

def calculate_maturity_scores(profile: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, float]:
    """
    1. Calculate maturity scoring using config-driven tool mappings.
    """
    tools = set(profile.get("current_digital_tools", []))
    mappings = rules.get("maturity_scoring", {}).get("tool_mappings", {})
    scores = {}

    dimensions = ["digital_presence", "productivity", "customer_management", "data_security", "ai_readiness"]
    
    for dim in dimensions:
        dim_mappings = mappings.get(dim, [])
        score = 1.0 # Default fallback
        for mapping in dim_mappings:
            required_tools = set(mapping.get("tools", []))
            if required_tools.issubset(tools):
                score = float(mapping.get("score", 1.0))
                break # First match is the highest score based on mapping order
        scores[dim] = score

    return scores

def calculate_weighted_maturity(scores: Dict[str, float], rules: Dict[str, Any]) -> float:
    """
    2. Weighted overall maturity
    """
    dimensions = rules.get("maturity_scoring", {}).get("dimensions", {})
    total_score = 0.0
    total_weight = 0.0
    
    for dim, score in scores.items():
        weight = dimensions.get(dim, {}).get("weight", 1.0)
        total_score += score * weight
        total_weight += weight
        
    if total_weight == 0:
        return 0.0
    
    return round(total_score / total_weight, 2)

def calculate_impact(hours_per_week: float, hourly_rate: float, rules: Dict[str, Any]) -> float | None:
    """
    3. Impact calculation
    Returns annual opportunity cost.
    """
    if hours_per_week is None or hourly_rate is None:
        return None
        
    sim_rules = rules.get("impact_simulation", {})
    weeks_per_year = sim_rules.get("weeks_per_year", 52)
    
    hours_per_year = hours_per_week * weeks_per_year
    annual_opportunity_cost = hours_per_year * hourly_rate
    
    return float(annual_opportunity_cost)

def classify_impact(annual_opportunity_cost: float | None, rules: Dict[str, Any]) -> str:
    """
    4. Impact classification
    """
    if annual_opportunity_cost is None:
        return "unestimated"
        
    thresholds = rules.get("impact_scoring", {}).get("annual_opportunity_cost_thresholds", {})
    
    for level, limits in thresholds.items():
        min_val = limits.get("min", 0)
        max_val = limits.get("max")
        
        if annual_opportunity_cost >= min_val:
            if max_val is None or annual_opportunity_cost <= max_val:
                return level
                
    return "low" # Fallback

def derive_urgency_signals(profile: Dict[str, Any], answers: List[Dict[str, Any]], rules: Dict[str, Any]) -> List[str]:
    """
    Map free-text assessment evidence to configured urgency signal tokens.
    """
    parts = [
        str(profile.get("industry", "")),
        " ".join(profile.get("main_operational_problems", [])),
    ]
    for entry in answers or []:
        parts.append(str(entry.get("answer", "")))

    text = " ".join(parts).lower()
    signals: List[str] = []

    keyword_to_signal = rules.get("urgency_scoring", {}).get("keywords", {})
    
    for keyword, signal in keyword_to_signal.items():
        if keyword in text:
            signals.append(signal)

    if not signals:
        signals.append("recurring_operational_problem")

    return list(dict.fromkeys(signals))


def classify_urgency(signals: List[str], rules: Dict[str, Any]) -> str:
    """
    5. Urgency classification
    """
    levels_dict = rules.get("urgency_scoring", {}).get("levels", {})
    
    highest_level = "low"
    highest_score = 0
    
    for level_name, level_data in levels_dict.items():
        level_score = level_data.get("score", 0)
        level_signals = level_data.get("signals", [])
        
        # Check if any signal from the SME matches this level's signals
        if any(s in level_signals for s in signals):
            if level_score > highest_score:
                highest_score = level_score
                highest_level = level_name
                
    return highest_level

def calculate_priority(impact_level: str, urgency_level: str, rules: Dict[str, Any]) -> int:
    """
    6. Priority matrix
    """
    matrix = rules.get("priority_matrix", {}).get("matrix", {})
    key = f"{impact_level}_{urgency_level}"
    return matrix.get(key, 5) # Default to lowest priority 5

def calculate_lead_score(impact_cost: float | None, urgency_level: str, maturity_score: float, rules: Dict[str, Any]) -> float:
    """
    7. Lead score
    """
    lead_rules = rules.get("lead_scoring", {})
    weights = lead_rules.get("weights", {})
    norms = lead_rules.get("normalisation", {})
    
    w_impact = weights.get("impact", 0.5)
    w_urgency = weights.get("urgency", 0.3)
    w_gap = weights.get("digitisation_gap", 0.2)
    
    # Normalise Impact
    impact_norm = 0
    if impact_cost is not None:
        impact_norm_rules = norms.get("impact", {})
        impact_thresholds = impact_norm_rules.get("thresholds", {})
        impact_cap = impact_norm_rules.get("cap_at", 100)
        
        # Sort thresholds descending to find the highest bracket
        sorted_thresholds = sorted([(float(k), v) for k, v in impact_thresholds.items()], reverse=True)
        for threshold_val, norm_val in sorted_thresholds:
            if impact_cost >= threshold_val:
                impact_norm = norm_val
                break
        impact_norm = min(impact_norm, impact_cap)
    
    # Normalise Urgency
    urgency_norm = norms.get("urgency", {}).get(urgency_level, 33)
    
    # Normalise Gap
    # "(5 - overall_maturity_score) / 5 * 100"
    gap_norm = ((5.0 - maturity_score) / 5.0) * 100.0
    
    lead_score = (w_impact * impact_norm) + (w_urgency * urgency_norm) + (w_gap * gap_norm)
    return round(lead_score, 2)

def generate_lead_score_reasons(impact_cost: float | None, urgency_level: str, maturity_score: float, rules: Dict[str, Any]) -> List[str]:
    """
    8. Lead score reasons
    """
    lead_rules = rules.get("lead_scoring", {})
    reason_rules = lead_rules.get("reason_rules", [])
    max_reasons = lead_rules.get("maximum_reasons", 4)
    
    # Recreate normalisation values for conditions
    gap_norm = ((5.0 - maturity_score) / 5.0) * 100.0
    impact_level = classify_impact(impact_cost, rules)
    
    evaluators = {
        "impact_level_is_high": lambda: impact_level == "high",
        "urgency_level_is_high": lambda: urgency_level == "high",
        "digitisation_gap_norm_is_at_least_60": lambda: gap_norm >= 60,
        "annual_opportunity_cost_is_at_least_20000": lambda: impact_cost is not None and impact_cost >= 20000,
        "multiple_maturity_dimensions_below_3": lambda: maturity_score < 3
    }
    
    reasons = []
    
    for rule in reason_rules:
        condition = rule.get("condition")
        reason = rule.get("reason")
        
        eval_fn = evaluators.get(condition)
        if eval_fn and eval_fn():
            if len(reasons) < max_reasons:
                reasons.append(reason)
            
    return reasons
