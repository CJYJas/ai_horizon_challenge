# Phase 6: API Examples

This document outlines example HTTP requests and responses for the Phase 6 Assessment API, using the "ABC Enterprise" scenario.

## 1. Start Assessment
Creates a new assessment session and persists the company profile.

**Request**
```http
POST /assessments
Content-Type: application/json

{
  "company_profile": {
    "industry": "Retail",
    "employee_count": 8,
    "current_digital_tools": ["whatsapp", "spreadsheet"],
    "main_operational_problems": ["Hard to keep track of customer orders"]
  }
}
```

**Response (200 OK)**
```json
{
  "assessment_id": "4f82a912-3b4c-4e81-8d2a-1c8a82d9f8b2",
  "status": "Created"
}
```

---

## 2. Submit Answer (Adaptive Loop)
Submits a single answer and triggers the AI Analyst chain to determine if more information is needed.

**Request**
```http
POST /assessments/4f82a912-3b4c-4e81-8d2a-1c8a82d9f8b2/answers
Content-Type: application/json

{
  "answer": "20 hrs/week"
}
```

**Response (200 OK - Gap Exists)**
```json
{
  "is_complete": false,
  "follow_up_question": "Do you lose enquiries/orders because multiple staff members handle WhatsApp separately?",
  "reason": "Need to understand revenue impact of fragmented communication."
}
```

*(When the loop finishes, `is_complete` will be `true` and `follow_up_question` will be `null`)*

---

## 3. Retrieve Diagnosis & Solutions
Executes deterministic scoring and solution matching.

**Request**
```http
GET /assessments/4f82a912-3b4c-4e81-8d2a-1c8a82d9f8b2/diagnosis
```

**Response (200 OK)**
```json
{
  "top_pain_points": [
    {
      "problem": "Hard to keep track of customer orders",
      "root_cause": "Fragmented digital operations",
      "evidence": ["See answers"],
      "business_impact": "~RM26000.0/year",
      "impact_estimate": "26000.0",
      "urgency": "high",
      "priority_rank": 1
    }
  ],
  "maturity_scores": {
    "digital_presence": 2.0,
    "productivity": 2.0,
    "customer_management": 2.0,
    "data_security": 1.0,
    "ai_readiness": 1.0
  },
  "recommendations": [
    {
      "product_id": "freshdesk",
      "linked_pain_point": "Hard to keep track of customer orders",
      "reason": "Matched FreshDesk based on the need to address: Hard to keep track of customer orders",
      "expected_outcome": "Helpdesk functionality"
    }
  ],
  "government_support": [
    {
      "support_id": "smecorp_sfsme_2_0",
      "linked_transformation": "digitalisation",
      "eligibility_status": "Potentially eligible"
    }
  ],
  "lead_score": 93.6
}
```

---

## 4. Run Impact Simulation
Deterministic recalculation of business impact based on user slider input.

**Request**
```http
POST /assessments/4f82a912-3b4c-4e81-8d2a-1c8a82d9f8b2/impact-simulation
Content-Type: application/json

{
  "hours_per_week": 20.0,
  "hourly_rate_assumption": 25.0,
  "automation_scenario_pct": 50.0
}
```

**Response (200 OK)**
```json
{
  "input_hours_per_week": 20.0,
  "hourly_rate_assumption": 25.0,
  "annual_opportunity_cost": 26000.0,
  "automation_scenario_pct": 50.0,
  "recovered_hours_per_year": 520.0,
  "recovered_value_per_year": 13000.0
}
```

---

## 5. Generate Narrative Report
Triggers the AI Strategist chain to generate the human-readable SME report and sales brief (caches the result in DB).

**Request**
```http
GET /assessments/4f82a912-3b4c-4e81-8d2a-1c8a82d9f8b2/report
```

**Response (200 OK)**
```json
{
  "report": {
    "pain_point_explanations": [
      {
        "problem": "Customer-order management bottleneck",
        "root_cause_explanation": "Fragmented tools",
        "why_it_matters": "High"
      }
    ],
    "roadmap_narrative": {
      "phase_1": "Phase 1: Implement Freshdesk",
      "phase_2": "Phase 2: Introduce automation",
      "phase_3": "Phase 3: Scale with AI"
    },
    "sme_report_summary": "Potentially eligible for government support.",
    "sales_brief": {
      "one_line_hook": "Hot lead based on high operational pain.",
      "why_this_lead_is_hot": [
        "High priority",
        "High opportunity cost"
      ],
      "recommended_approach": "Lead with time-saving solutions."
    }
  }
}
```

---

## 6. List Sales Leads
Returns deterministic lead cards sorted by score.

**Request**
```http
GET /leads
```

**Response (200 OK)**
```json
[
  {
    "assessment_id": "4f82a912-3b4c-4e81-8d2a-1c8a82d9f8b2",
    "company_industry": "Retail",
    "employee_count": 8,
    "lead_score": 93.6,
    "top_pain_point_problem": "Customer-order management bottleneck",
    "created_at": "2026-09-15T21:00:00+00:00"
  }
]
```

---

## 7. Get Lead Details
Returns details and sales brief for a specific lead.

**Request**
```http
GET /leads/4f82a912-3b4c-4e81-8d2a-1c8a82d9f8b2
```

**Response (200 OK)**
```json
{
  "assessment_id": "4f82a912-3b4c-4e81-8d2a-1c8a82d9f8b2",
  "company_profile": {
    "industry": "Retail",
    "employee_count": 8,
    "current_digital_tools": ["whatsapp", "spreadsheet"],
    "main_operational_problems": ["Hard to keep track of customer orders"]
  },
  "lead_score": 93.6,
  "lead_score_reasons": ["High priority", "High opportunity cost"],
  "sales_brief": {
    "why_this_lead_is_hot": ["High priority", "High opportunity cost"]
  }
}
```
