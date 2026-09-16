from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, JSON

# --- Pydantic sub-models for nested JSON fields in SMEAssessment ---

class CompanyProfile(BaseModel):
    industry: str
    employee_count: int
    current_digital_tools: List[str]
    main_operational_problems: List[str]

class BusinessContext(BaseModel):
    monthly_revenue_range: Optional[str] = None
    growth_stage: Optional[str] = None
    online_sales: Optional[bool] = None

class Answer(BaseModel):
    question_id: str
    question_text: str
    answer: Union[str, int, bool]
    asked_reason: str

class TopPainPoint(BaseModel):
    problem: str
    root_cause: str
    evidence: List[str]
    business_impact: str
    impact_estimate: str
    urgency: str
    priority_rank: int

class Diagnosis(BaseModel):
    top_pain_points: List[TopPainPoint]

class MaturityScores(BaseModel):
    digital_presence: float
    productivity: float
    customer_management: float
    data_security: float
    ai_readiness: float

class ImpactSimulation(BaseModel):
    input_hours_per_week: float
    hourly_rate_assumption: float
    annual_opportunity_cost: float
    automation_scenario_pct: float
    recovered_hours_per_year: float
    recovered_value_per_year: float

class Recommendation(BaseModel):
    product_id: str
    linked_pain_point: str
    reason: str
    expected_outcome: str

class GovernmentSupportMatch(BaseModel):
    support_id: str
    linked_transformation: str
    eligibility_status: str


# --- SQLModel for SQLite Database Persistence ---

class SMEAssessment(SQLModel, table=True):
    __tablename__ = "sme_assessments"
    
    assessment_id: str = Field(primary_key=True)
    created_at: str
    
    # Store complex structures as JSON
    company_profile: dict = Field(default_factory=dict, sa_column=Column(JSON))
    business_context: dict = Field(default_factory=dict, sa_column=Column(JSON))
    answers: list = Field(default_factory=list, sa_column=Column(JSON))
    diagnosis: dict = Field(default_factory=dict, sa_column=Column(JSON))
    maturity_scores: dict = Field(default_factory=dict, sa_column=Column(JSON))
    impact_simulation: dict = Field(default_factory=dict, sa_column=Column(JSON))
    recommendations: list = Field(default_factory=list, sa_column=Column(JSON))
    government_support: list = Field(default_factory=list, sa_column=Column(JSON))
    
    lead_score: float = Field(default=0.0)
    lead_score_reasons: list = Field(default_factory=list, sa_column=Column(JSON))
    sales_brief: dict = Field(default_factory=dict, sa_column=Column(JSON))


# --- Pydantic Models for /data JSON loading ---

class ExabytesProduct(BaseModel):
    product_id: str
    name: str
    category: str
    transformation_stage: str
    target_business: List[str]
    problems_solved: List[str]
    benefits: List[str]
    prerequisites: List[str]
    pricing: Optional[str] = None
    grant_categories: List[str]
    source_url: str
    source_date: str
    confidence: str

class GovernmentSupportModel(BaseModel):
    support_id: str
    programme: str
    support_type: str
    source: str
    source_url: str
    last_verified: str
    conditions: List[str]
    coverage: str
    maximum_amount: Optional[str] = None
    minimum_amount: Optional[str] = None
    eligible_categories: List[str]
    eligibility_note: str
    system_use: str

class SupportingRules(BaseModel):
    version: str
    last_updated: str
    maturity_scoring: Dict[str, Any]
    priority_matrix: Dict[str, Any]
    lead_scoring: Dict[str, Any]
    impact_simulation: Dict[str, Any]
    # Optionally catch additional keys
    model_config = {"extra": "allow"}
