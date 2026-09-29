import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from backend.main import app
from backend.database import get_session

test_engine = create_engine("sqlite:///./test_demo_flow.db")


def get_test_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = get_test_session
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


def test_demo_scenario_full_pipeline():
    """
    Test the canonical demo flow documented in docs/mock_flow.md
    from assessment creation to sales dashboard presentation.
    """
    # 1. Enter Demo Mode / retrieve demo case configuration
    case_res = client.get("/demo/case")
    assert case_res.status_code == 200
    case_data = case_res.json()
    assert case_data["company_profile"]["company_name"] == "ABC Enterprise"
    assert case_data["company_profile"]["industry"] == "Retail"
    assert case_data["company_profile"]["employee_count"] == 8

    # 2. Create Demo Assessment
    create_res = client.post("/demo/assessments")
    assert create_res.status_code == 200
    created = create_res.json()
    assert "assessment_id" in created
    assessment_id = created["assessment_id"]
    assert assessment_id.startswith("demo-")
    assert "tools" in created["initial_question"].lower() or "workflow" in created["initial_question"].lower()

    # 3. Submit Answer 1
    a1_res = client.post(f"/demo/assessments/{assessment_id}/answers", json={
        "answer": "WhatsApp and spreadsheets",
        "question_text": created["initial_question"],
        "question_topic": created["initial_question_topic"]
    })
    assert a1_res.status_code == 200
    a1_data = a1_res.json()
    assert a1_data["is_complete"] is False
    assert "hours" in a1_data["follow_up_question"].lower()

    # 4. Submit Answer 2
    a2_res = client.post(f"/demo/assessments/{assessment_id}/answers", json={
        "answer": "About 20 hours a week",
        "question_text": a1_data["follow_up_question"],
        "question_topic": a1_data["question_topic"]
    })
    assert a2_res.status_code == 200
    a2_data = a2_res.json()
    assert a2_data["is_complete"] is False
    assert "whatsapp" in a2_data["follow_up_question"].lower() or "lose" in a2_data["follow_up_question"].lower()

    # 5. Submit Answer 3 -> complete
    a3_res = client.post(f"/demo/assessments/{assessment_id}/answers", json={
        "answer": "Yes, we miss messages regularly",
        "question_text": a2_data["follow_up_question"],
        "question_topic": a2_data["question_topic"]
    })
    assert a3_res.status_code == 200
    a3_data = a3_res.json()
    assert a3_data["is_complete"] is True

    # 6. Diagnosis appears
    diag_res = client.get(f"/demo/assessments/{assessment_id}/diagnosis")
    assert diag_res.status_code == 200
    diag = diag_res.json()

    # Maturity scores: digital_presence: 2, productivity: 2, customer_management: 2, data_security: 1, ai_readiness: 1
    scores = diag["maturity_scores"]
    assert scores["digital_presence"] == 2.0
    assert scores["productivity"] == 2.0
    assert scores["customer_management"] == 2.0
    assert scores["data_security"] == 1.0
    assert scores["ai_readiness"] == 1.0

    # Lead score before simulation is 33.24
    assert diag["lead_score"] == 33.24

    # Solution matching: Freshsales wins
    rec_ids = [r["product_id"] for r in diag["recommendations"]]
    assert "freshsales" in rec_ids

    # Government matching: SFSME 2.0
    gov_ids = [g["support_id"] for g in diag["government_support"]]
    assert "smecorp_sfsme_2_0" in gov_ids

    # 7. Impact simulation
    sim_res = client.post(f"/demo/assessments/{assessment_id}/impact-simulation", json={
        "hours_per_week": 20.0,
        "hourly_rate_assumption": 25.0,
        "automation_scenario_pct": 50.0
    })
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert sim_data["annual_opportunity_cost"] == 26000.0  # 20 * 52 * 25
    assert sim_data["recovered_hours_per_year"] == 520.0
    assert sim_data["recovered_value_per_year"] == 13000.0

    # 8. Report reflects updated lead score and roadmap
    rep_res = client.get(f"/demo/assessments/{assessment_id}/report")
    assert rep_res.status_code == 200
    rep = rep_res.json()
    assert rep["diagnosis_data"]["lead_score"] == 70.74
    assert "freshsales" in rep["report"]["roadmap_narrative"]["phase_1"].lower()

    # 9. Lead dashboard displays lead
    leads_res = client.get("/leads")
    assert leads_res.status_code == 200
    leads = leads_res.json()
    demo_lead = next((l for l in leads if l["assessment_id"] == assessment_id), None)
    assert demo_lead is not None
    assert demo_lead["company_name"] == "ABC Enterprise"
    assert demo_lead["lead_score"] == 70.74
    assert demo_lead["priority"] == 2

    # 10. Sales report playbook
    sales_res = client.get(f"/leads/{assessment_id}/sales-report")
    assert sales_res.status_code == 200
    sales_data = sales_res.json()
    assert sales_data["company_profile"]["company_name"] == "ABC Enterprise"
    assert "Retail" in sales_data["lead_label"]
    assert len(sales_data["report"]["sales_playbook"]["discovery_questions"]) > 0


def test_standard_endpoints_handle_demo_gracefully():
    """
    Verify that calling standard endpoints with a demo assessment ID
    works identically and deterministically.
    """
    create_res = client.post("/demo/assessments")
    assessment_id = create_res.json()["assessment_id"]

    # Submit via standard /assessments/{id}/answers
    a1 = client.post(f"/assessments/{assessment_id}/answers", json={
        "answer": "WhatsApp and spreadsheets"
    })
    assert a1.status_code == 200
    assert a1.json()["is_complete"] is False

    a2 = client.post(f"/assessments/{assessment_id}/answers", json={
        "answer": "About 20 hours a week"
    })
    assert a2.status_code == 200
    assert a2.json()["is_complete"] is False

    a3 = client.post(f"/assessments/{assessment_id}/answers", json={
        "answer": "Yes, we miss messages regularly"
    })
    assert a3.status_code == 200
    assert a3.json()["is_complete"] is True

    # Standard diagnosis
    diag = client.get(f"/assessments/{assessment_id}/diagnosis")
    assert diag.status_code == 200
    assert diag.json()["lead_score"] == 33.24
