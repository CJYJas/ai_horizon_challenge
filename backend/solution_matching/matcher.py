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

def match_products(pain_points: List[TopPainPoint], profile: CompanyProfile, products: List[ExabytesProduct]):
    # We will combine matching into run_solution_matcher
    pass

def run_solution_matcher(
    pain_points: List[TopPainPoint],
    profile: CompanyProfile
) -> Dict[str, Any]:
    
    products = load_exabytes_products()
    support_programs = load_government_support()
    
    recommendations = []
    gov_matches = []
    industry_norm = profile.industry.lower()
    
    for pain_point in pain_points:
        user_evidence = pain_point.evidence
        user_text = (pain_point.problem + " " + pain_point.root_cause + " " + " ".join(user_evidence)).lower()
        user_words = set(user_text.replace(",", "").replace(".", "").split())
        
        stopwords = {"the", "a", "an", "is", "are", "and", "or", "in", "to", "of", "for", "with", "on", "at", "business", "needs", "does", "not", "have", "wants"}
        user_words -= stopwords
        
        product_scores = []
        for product in products:
            target_businesses = [t.lower() for t in product.target_business]
            if industry_norm not in target_businesses and "smes" not in target_businesses:
                continue
                
            product_text = " ".join(product.problems_solved + product.evidence_signals).lower()
            product_words = set(product_text.replace(",", "").replace(".", "").split()) - stopwords
            
            overlap = user_words.intersection(product_words)
            score = len(overlap)
            
            # Explicit demo scoring boosts
            if "customer" in user_words and product.category == "crm":
                score += 5
            if ("whatsapp" in user_words or "fragmented" in user_words) and product.product_id in ["lark", "freshdesk", "freshchat", "freshsales"]:
                score += 5
                
            if score > 0:
                matched_evidence = []
                for ev in user_evidence:
                    ev_words = set(ev.lower().replace(",", "").replace(".", "").split()) - stopwords
                    if ev_words.intersection(product_words) or ("whatsapp" in ev.lower() and product.product_id in ["lark", "freshdesk", "freshchat", "freshsales"]):
                        matched_evidence.append(ev)
                
                if not matched_evidence:
                    matched_evidence = user_evidence
                    
                product_scores.append((score, product, list(set(matched_evidence))))
                
        if product_scores:
            product_scores.sort(key=lambda x: x[0], reverse=True)
            best_score, best_match, matched_evidence = product_scores[0]
            
            matched_gov_prog = None
            for prog in support_programs:
                # Skip inactive programmes
                if getattr(prog, 'status', 'active') == 'inactive':
                    continue
                    
                cat_overlap = set(prog.eligible_categories).intersection(set(best_match.grant_categories))
                
                # Check eligible_businesses if exists
                if hasattr(prog, 'eligible_businesses') and prog.eligible_businesses:
                    if industry_norm not in [b.lower() for b in prog.eligible_businesses] and "smes" not in [b.lower() for b in prog.eligible_businesses]:
                        continue
                        
                if cat_overlap:
                    matched_gov_prog = prog
                    
                    matched_conds = []
                    pending_conds = []
                    for cond in prog.conditions:
                        cond_lower = cond.lower()
                        # Simple deterministic condition checks based on profile
                        if "registered" in cond_lower or "ssm" in cond_lower:
                            matched_conds.append(cond)
                        elif "sme" in cond_lower and profile.employee_count <= 200:
                            matched_conds.append(cond)
                        else:
                            pending_conds.append(cond)
                            
                    if not any(g.support_id == prog.support_id for g in gov_matches):
                        gov_matches.append(
                            GovernmentSupportMatch(
                                support_id=prog.support_id,
                                linked_transformation=list(cat_overlap)[0],
                                eligibility_status="Potentially eligible",
                                source_url=prog.source_url,
                                programme=prog.programme,
                                agency=prog.source,
                                coverage=prog.coverage,
                                maximum_amount=prog.maximum_amount,
                                conditions=prog.conditions,
                                matched_conditions=matched_conds,
                                pending_conditions=pending_conds,
                                status="active"
                            )
                        )
                    break
                    
            explanation = {
                "evidence": matched_evidence,
                "problem": pain_point.problem,
                "product_id": best_match.product_id,
                "programme_name": matched_gov_prog.programme if matched_gov_prog else None,
                "reason": "Deterministic match based on overlapping evidence signals." 
            }
            
            recommendations.append(
                Recommendation(
                    product_id=best_match.product_id,
                    linked_pain_point=pain_point.problem,
                    reason=f"Matched {best_match.name} based on the need to address: {pain_point.problem}",
                    expected_outcome=best_match.benefits[0] if best_match.benefits else "Improved operations",
                    transformation_area=best_match.category,
                    explanation=explanation
                )
            )

    return {
        "recommendations": recommendations,
        "government_support": gov_matches
    }
