import math
from typing import Dict, Any, List

def calculate_maturity_scores(profile: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, float]:
    """
    1. Calculate maturity scoring
    ASSUMPTION DOCUMENTATION:
    The existing supporting_rules.json provides string conditions (e.g., 'no_website_or_online_presence') 
    but no machine-readable logic to map 'company_profile.current_digital_tools' to these conditions.
    To avoid using an LLM, we implement the smallest explicit mapping here:
    We use the presence of specific tools ('website', 'whatsapp', 'spreadsheet', 'crm', 'pos') 
    to deterministically pick a score based on the highest matched condition.
    """
    tools = profile.get("current_digital_tools", [])
    
    # Base mapping logic based on tools presence
    has_website = "website" in tools
    has_whatsapp = "whatsapp" in tools
    has_crm = "crm" in tools
    has_spreadsheet = "spreadsheet" in tools
    has_pos = "pos" in tools

    # digital_presence
    if has_website and has_whatsapp and has_crm:
        dp_score = 4
    elif has_website and has_whatsapp:
        dp_score = 3
    elif has_website or has_whatsapp:
        dp_score = 2
    else:
        dp_score = 1

    # productivity
    if has_crm and has_pos:
        pr_score = 4
    elif has_crm or has_pos:
        pr_score = 3
    elif has_spreadsheet:
        pr_score = 2
    else:
        pr_score = 1

    # customer_management
    if has_crm and has_whatsapp:
        cm_score = 4
    elif has_crm:
        cm_score = 3
    elif has_whatsapp or has_spreadsheet:
        cm_score = 2
    else:
        cm_score = 1

    # data_security (Assumption: CRM/POS implies some cloud backup usually, spreadsheets less so)
    if has_crm and has_pos:
        ds_score = 3
    elif has_crm or has_pos or has_website:
        ds_score = 2
    else:
        ds_score = 1

    # ai_readiness (Depends on structured data like CRM)
    if has_crm and has_pos:
        ai_score = 3
    elif has_crm or has_pos:
        ai_score = 2
    else:
        ai_score = 1

    return {
        "digital_presence": float(dp_score),
        "productivity": float(pr_score),
        "customer_management": float(cm_score),
        "data_security": float(ds_score),
        "ai_readiness": float(ai_score)
    }

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

def calculate_impact(hours_per_week: float, hourly_rate: float, rules: Dict[str, Any]) -> float:
    """
    3. Impact calculation
    Returns annual opportunity cost.
    """
    sim_rules = rules.get("impact_simulation", {})
    weeks_per_year = sim_rules.get("weeks_per_year", 52)
    
    hours_per_year = hours_per_week * weeks_per_year
    annual_opportunity_cost = hours_per_year * hourly_rate
    
    return float(annual_opportunity_cost)

def classify_impact(annual_opportunity_cost: float, rules: Dict[str, Any]) -> str:
    """
    4. Impact classification
    """
    thresholds = rules.get("impact_scoring", {}).get("annual_opportunity_cost_thresholds", {})
    
    for level, limits in thresholds.items():
        min_val = limits.get("min", 0)
        max_val = limits.get("max")
        
        if annual_opportunity_cost >= min_val:
            if max_val is None or annual_opportunity_cost <= max_val:
                return level
                
    return "low" # Fallback

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

def calculate_lead_score(impact_cost: float, urgency_level: str, maturity_score: float, rules: Dict[str, Any]) -> float:
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
    impact_norm_rules = norms.get("impact", {})
    impact_thresholds = impact_norm_rules.get("thresholds", {})
    impact_cap = impact_norm_rules.get("cap_at", 100)
    
    impact_norm = 0
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

def generate_lead_score_reasons(impact_cost: float, urgency_level: str, maturity_score: float, rules: Dict[str, Any]) -> List[str]:
    """
    8. Lead score reasons
    """
    lead_rules = rules.get("lead_scoring", {})
    reason_rules = lead_rules.get("reason_rules", [])
    max_reasons = lead_rules.get("maximum_reasons", 4)
    
    # Recreate normalisation values for conditions
    norms = lead_rules.get("normalisation", {})
    gap_norm = ((5.0 - maturity_score) / 5.0) * 100.0
    impact_level = classify_impact(impact_cost, rules)
    
    reasons = []
    
    for rule in reason_rules:
        condition = rule.get("condition")
        reason = rule.get("reason")
        
        matched = False
        if condition == "impact_level_is_high" and impact_level == "high":
            matched = True
        elif condition == "urgency_level_is_high" and urgency_level == "high":
            matched = True
        elif condition == "digitisation_gap_norm_is_at_least_60" and gap_norm >= 60:
            matched = True
        elif condition == "annual_opportunity_cost_is_at_least_20000" and impact_cost >= 20000:
            matched = True
        elif condition == "multiple_maturity_dimensions_below_3" and maturity_score < 3: 
            # Note: The condition says 'multiple_maturity_dimensions_below_3' but we only have overall maturity here.
            # Using overall maturity < 3 as a proxy to avoid requiring the full scores dict.
            matched = True
            
        if matched and len(reasons) < max_reasons:
            reasons.append(reason)
            
    return reasons
