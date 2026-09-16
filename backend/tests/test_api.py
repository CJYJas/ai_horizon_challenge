import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from backend.main import app
from backend.database import get_session

# Ensure we have a real LLM API key as requested by the user
if not os.getenv("OPENAI_API_KEY"):
    pytest.skip("Skipping API tests because OPENAI_API_KEY is not set", allow_module_level=True)

engine = create_engine("sqlite:///./test_assessment_api.db")

def get_session_override():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = get_session_override

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

def test_api_pipeline():
    # 1. Start Assessment
    res = client.post("/assessments", json={
        "company_profile": {
            "industry": "Retail",
            "employee_count": 8,
            "current_digital_tools": ["whatsapp", "spreadsheet"],
            "main_operational_problems": ["Hard to keep track of customer orders"]
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert "assessment_id" in data
    assert data["status"] == "Created"
    
    assessment_id = data["assessment_id"]
    
    # 2. Submit Answers (Trigger real Analyst LLM)
    res = client.post(f"/assessments/{assessment_id}/answers", json={
        "answer": "We manage orders entirely manually across whatsapp and excel, taking 20 hours a week."
    })
    assert res.status_code == 200
    ans_data = res.json()
    assert "is_complete" in ans_data
    
    # 3. Retrieve Diagnosis
    res = client.get(f"/assessments/{assessment_id}/diagnosis")
    assert res.status_code == 200
    diag = res.json()
    assert "lead_score" in diag
    assert "recommendations" in diag
    
    # 4. Impact Simulation (Deterministic recalculation)
    res = client.post(f"/assessments/{assessment_id}/impact-simulation", json={
        "hours_per_week": 20.0,
        "hourly_rate_assumption": 25.0,
        "automation_scenario_pct": 50.0
    })
    assert res.status_code == 200
    sim_data = res.json()
    assert sim_data["annual_opportunity_cost"] == 26000.0 # 20 * 52 * 25
    assert sim_data["recovered_value_per_year"] == 13000.0
    
    # 5. Generate Report (Trigger real Strategist LLM)
    res = client.get(f"/assessments/{assessment_id}/report")
    assert res.status_code == 200
    rep = res.json()
    assert "report" in rep
    assert "pain_point_explanations" in rep["report"]
    
    # 6. List Leads
    res = client.get("/leads")
    assert res.status_code == 200
    leads = res.json()
    assert len(leads) == 1
    assert leads[0]["assessment_id"] == assessment_id
    
    # 7. Get Lead Details
    res = client.get(f"/leads/{assessment_id}")
    assert res.status_code == 200
    lead_detail = res.json()
    assert "company_profile" in lead_detail
    assert "sales_brief" in lead_detail

def test_invalid_assessment():
    res = client.get("/assessments/invalid-id/diagnosis")
    assert res.status_code == 404
