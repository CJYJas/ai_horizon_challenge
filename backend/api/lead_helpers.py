from typing import Any, Dict, List

from backend.models import TopPainPoint, Recommendation


def format_lead_label(profile: Dict[str, Any], assessment_id: str) -> str:
    """Display label for pipeline rows — business context only, no personal identifiers."""
    industry = profile.get("industry") or "SME"
    problems = profile.get("main_operational_problems") or []
    if problems:
        headline = problems[0]
        if len(headline) > 52:
            headline = headline[:49] + "..."
        return f"{industry} · {headline}"
    employees = profile.get("employee_count")
    emp_part = f"{employees} staff" if employees is not None else "unknown size"
    short_id = assessment_id.replace("-", "")[:6].upper()
    return f"{industry} · {emp_part} · #{short_id}"


def normalize_sales_brief(
    brief: Dict[str, Any],
    profile: Dict[str, Any],
    pain_points: List[TopPainPoint],
    lead_score_reasons: List[str],
    recommendations: List[Recommendation],
) -> Dict[str, Any]:
    merged = dict(brief or {})
    main_problem = (
        pain_points[0].problem
        if pain_points
        else (profile.get("main_operational_problems") or ["Operational bottlenecks"])[0]
    )
    industry = profile.get("industry", "SME")
    employees = profile.get("employee_count")
    tools = profile.get("current_digital_tools") or []
    tools_text = ", ".join(tools) if tools else "limited digital tooling"

    hot = merged.get("why_this_lead_is_hot") or lead_score_reasons or []
    if not hot:
        hot = [f"Primary bottleneck: {main_problem[:120]}"]

    situation = merged.get("sme_situation_summary") or merged.get("one_line_hook")
    if not situation:
        situation = (
            f"A {industry} business (~{employees} employees) is constrained by: {main_problem}. "
            f"Current tools ({tools_text}) create fragmentation and manual overhead."
        )

    angle = merged.get("suggested_conversation_angle") or merged.get("recommended_approach")
    if not angle:
        product = recommendations[0].product_id.upper() if recommendations else "the recommended Exabytes stack"
        angle = (
            f"Open with measurable time savings: show how {product} directly reduces friction around "
            f"\"{main_problem[:100]}\" without a disruptive rip-and-replace."
        )

    return {
        **merged,
        "one_line_hook": merged.get("one_line_hook") or situation[:160],
        "why_this_lead_is_hot": hot,
        "recommended_approach": merged.get("recommended_approach") or angle,
        "sme_situation_summary": situation,
        "suggested_conversation_angle": angle,
    }
