import pytest
from datetime import datetime, timezone
from sqlmodel import Session, create_engine, SQLModel
from backend.models import (
    SMEAssessment,
    CompanyProfile,
    BusinessContext,
    Answer,
    TopPainPoint,
    Diagnosis,
    MaturityScores,
    ImpactSimulation
)
from backend.data_loaders import (
    load_exabytes_products,
    load_government_support,
    load_supporting_rules
)

# Test DB Engine
test_engine = create_engine("sqlite:///:memory:")

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)

def test_create_and_load_assessment(session: Session):
    # Setup dummy data using Pydantic models to ensure validity, then dumping to dict
    profile = CompanyProfile(
        industry="Retail",
        employee_count=10,
        current_digital_tools=["website", "whatsapp"],
        main_operational_problems=["Inventory tracking"]
    )
    
    answer = Answer(
        question_id="q1",
        question_text="How do you track inventory?",
        answer="spreadsheet",
        asked_reason="To understand manual labor"
    )
    
    pain = TopPainPoint(
        problem="Manual inventory takes too long",
        root_cause="No POS integration",
        evidence=["Use spreadsheets"],
        business_impact="High error rate",
        impact_estimate="RM 1000/mo",
        urgency="high",
        priority_rank=1
    )
    
    diagnosis = Diagnosis(top_pain_points=[pain])
    
    scores = MaturityScores(
        digital_presence=3.0,
        productivity=2.0,
        customer_management=1.5,
        data_security=2.0,
        ai_readiness=1.0
    )
    
    impact = ImpactSimulation(
        input_hours_per_week=20.0,
        hourly_rate_assumption=50.0,
        annual_opportunity_cost=52000.0,
        automation_scenario_pct=0.5,
        recovered_hours_per_year=520.0,
        recovered_value_per_year=26000.0
    )
    
    assessment = SMEAssessment(
        assessment_id="test-uuid-1234",
        created_at=datetime.now(timezone.utc).isoformat(),
        company_profile=profile.model_dump(),
        business_context=BusinessContext(growth_stage="early").model_dump(),
        answers=[answer.model_dump()],
        diagnosis=diagnosis.model_dump(),
        maturity_scores=scores.model_dump(),
        impact_simulation=impact.model_dump(),
        recommendations=[],
        government_support=[],
        lead_score=85.5,
        lead_score_reasons=["High urgency", "Ready for digital"]
    )
    
    # Save
    session.add(assessment)
    session.commit()
    session.refresh(assessment)
    
    # Load
    loaded = session.get(SMEAssessment, "test-uuid-1234")
    assert loaded is not None
    assert loaded.lead_score == 85.5
    assert loaded.company_profile["industry"] == "Retail"
    assert loaded.diagnosis["top_pain_points"][0]["priority_rank"] == 1
    assert len(loaded.answers) == 1

def test_load_data_json():
    products = load_exabytes_products()
    assert len(products) > 0
    assert hasattr(products[0], "product_id")

    support = load_government_support()
    assert len(support) > 0
    assert hasattr(support[0], "support_id")

    rules = load_supporting_rules()
    assert rules.version is not None
    assert isinstance(rules.maturity_scoring, dict)
