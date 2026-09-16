from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel
from backend.models import (
    CompanyProfile, 
    MaturityScores, 
    TopPainPoint, 
    Recommendation, 
    GovernmentSupportMatch
)
from backend.ai_chains.strategist import StrategistOutput

class CreateAssessmentRequest(BaseModel):
    company_profile: CompanyProfile

class CreateAssessmentResponse(BaseModel):
    assessment_id: str
    status: str

class AnswerRequest(BaseModel):
    answer: Union[str, int, bool]

class AnswerResponse(BaseModel):
    is_complete: bool
    follow_up_question: Optional[str] = None
    reason: Optional[str] = None

class DiagnosisResponse(BaseModel):
    top_pain_points: List[TopPainPoint]
    maturity_scores: MaturityScores
    recommendations: List[Recommendation]
    government_support: List[GovernmentSupportMatch]
    lead_score: float

class ImpactSimulationRequest(BaseModel):
    hours_per_week: float
    hourly_rate_assumption: float
    automation_scenario_pct: float

class ImpactSimulationResponse(BaseModel):
    input_hours_per_week: float
    hourly_rate_assumption: float
    annual_opportunity_cost: float
    automation_scenario_pct: float
    recovered_hours_per_year: float
    recovered_value_per_year: float

class ReportResponse(BaseModel):
    report: StrategistOutput
    company_profile: CompanyProfile
    diagnosis_data: DiagnosisResponse
    impact_simulation: Optional[ImpactSimulationResponse] = None

class LeadCardResponse(BaseModel):
    assessment_id: str
    company_name: str
    company_industry: str
    employee_count: int
    overall_maturity: float
    lead_score: float
    priority: int
    top_pain_point_problem: Optional[str] = None
    recommended_transformation: Optional[str] = None
    created_at: str

class LeadDetailResponse(BaseModel):
    assessment_id: str
    company_profile: CompanyProfile
    lead_score: float
    lead_score_reasons: List[str]
    sales_brief: Dict[str, Any]
    diagnosis_data: DiagnosisResponse
    impact_simulation: Optional[ImpactSimulationResponse] = None
