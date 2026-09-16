from typing import List, Dict, Any
from backend.models import (
    TopPainPoint, 
    CompanyProfile, 
    ExabytesProduct, 
    GovernmentSupportModel,
    Recommendation,
    GovernmentSupportMatch
)
from backend.data_loaders import load_exabytes_products, load_government_support

def match_products(
    pain_points: List[TopPainPoint],
    profile: CompanyProfile,
    products: List[ExabytesProduct]
) -> List[Recommendation]:
    """
    Deterministic matching of products to pain points.
    Matches using keywords found in the pain point problem/root cause and the product's problems_solved.
    """
    recommendations = []
    
    for pain_point in pain_points:
        best_match = None
        highest_score = 0
        
        pain_point_text = (pain_point.problem + " " + pain_point.root_cause).lower()
        
        # Simple keywords to boost matching
        keywords = set(pain_point_text.replace(",", "").replace(".", "").split())
        
        for product in products:
            # Check industry match
            industry_match = profile.industry.lower() in [t.lower() for t in product.target_business] or "smes" in [t.lower() for t in product.target_business]
            
            if not industry_match:
                continue
                
            score = 0
            for prob in product.problems_solved:
                prob_lower = prob.lower()
                for kw in keywords:
                    if len(kw) > 4 and kw in prob_lower:
                        score += 1
                        
            # Exact matches for demo scenario
            if "customer" in keywords and product.category == "crm":
                score += 5
            if ("whatsapp" in keywords or "fragmented" in keywords) and product.product_id in ["lark", "freshdesk", "freshchat"]:
                score += 5
                
            if score > highest_score:
                highest_score = score
                best_match = product
                
        if best_match:
            recommendations.append(
                Recommendation(
                    product_id=best_match.product_id,
                    linked_pain_point=pain_point.problem,
                    reason=f"Matched {best_match.name} based on the need to address: {pain_point.problem}",
                    expected_outcome=best_match.benefits[0] if best_match.benefits else "Improved operations"
                )
            )
            
    return recommendations

def match_government_support(
    pain_points: List[TopPainPoint],
    support_programs: List[GovernmentSupportModel]
) -> List[GovernmentSupportMatch]:
    """
    Deterministic matching of government support.
    """
    matches = []
    
    # Extract general themes from pain points
    themes = set()
    for pp in pain_points:
        text = (pp.problem + " " + pp.root_cause).lower()
        if "manual" in text or "automate" in text or "whatsapp" in text or "spreadsheet" in text:
            themes.add("digitalisation")
            themes.add("automation")
        if "train" in text or "staff" in text or "employee" in text:
            themes.add("employee_training")
            themes.add("digital_skills")
            
    for prog in support_programs:
        overlap = set(prog.eligible_categories).intersection(themes)
        if overlap:
            matches.append(
                GovernmentSupportMatch(
                    support_id=prog.support_id,
                    linked_transformation=list(overlap)[0],
                    eligibility_status="Potentially eligible"
                )
            )
            
    return matches

def run_solution_matcher(
    pain_points: List[TopPainPoint],
    profile: CompanyProfile
) -> Dict[str, Any]:
    
    products = load_exabytes_products()
    support = load_government_support()
    
    product_recs = match_products(pain_points, profile, products)
    gov_matches = match_government_support(pain_points, support)
    
    return {
        "recommendations": product_recs,
        "government_support": gov_matches
    }
