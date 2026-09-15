# 05. Data Schema

The system uses structured JSON files for product, government support, and business rules. The persisted SME assessment stores the user's responses, AI diagnosis, deterministic calculations, recommendations, and sales-prioritisation results.

All JSON files are stored in `/data` and loaded by the Python backend. Business rules should not be hardcoded into `if/else` branches.

---

## 1. SME Assessment — Persisted Record

The assessment represents one SME's digital transformation diagnosis from initial questionnaire through final recommendations.

```json
{
  "assessment_id": "string (uuid)",
  "created_at": "ISO 8601 timestamp",

  "company_profile": {
    "industry": "string",
    "employee_count": "number",
    "current_digital_tools": [
      "website",
      "whatsapp",
      "spreadsheet",
      "crm",
      "pos"
    ],
    "main_operational_problems": [
      "string",
      "..."
    ]
  },

  "business_context": {
    "monthly_revenue_range": "string | null",
    "growth_stage": "string | null",
    "online_sales": "boolean | null"
  },

  "answers": [
    {
      "question_id": "string",
      "question_text": "string",
      "answer": "string | number | boolean",
      "asked_reason": "string (why the AI asked this question — for transparency/debugging)"
    }
  ],

  "diagnosis": {
    "top_pain_points": [
      {
        "problem": "string",
        "root_cause": "string",
        "evidence": [
          "string",
          "..."
        ],
        "business_impact": "string",
        "impact_estimate": "string",
        "urgency": "low | medium | high",
        "priority_rank": "number"
      }
    ]
  },

  "maturity_scores": {
    "digital_presence": "number (0-5)",
    "productivity": "number (0-5)",
    "customer_management": "number (0-5)",
    "data_security": "number (0-5)",
    "ai_readiness": "number (0-5)"
  },

  "impact_simulation": {
    "input_hours_per_week": "number",
    "hourly_rate_assumption": "number",
    "annual_opportunity_cost": "number",
    "automation_scenario_pct": "number",
    "recovered_hours_per_year": "number",
    "recovered_value_per_year": "number"
  },

  "recommendations": [
    {
      "product_id": "string (references exabytes_products.json)",
      "linked_pain_point": "string",
      "reason": "string",
      "expected_outcome": "string"
    }
  ],

  "government_support": [
    {
      "support_id": "string (references government_support.json)",
      "linked_transformation": "string",
      "eligibility_status": "potentially_eligible | not_matched | requires_verification"
    }
  ],

  "lead_score": "number (0-100)",

  "lead_score_reasons": [
    "string",
    "..."
  ]
}
```

### Key design principles

* `answers` stores the complete adaptive assessment history.
* `asked_reason` records why a follow-up question was generated. This is mainly for transparency and debugging.
* `evidence` connects the diagnosis to information provided by the SME.
* `root_cause` prevents the system from simply matching an industry to a product.
* `priority_rank` is calculated using the deterministic priority matrix.
* `impact_simulation` contains deterministic calculations from `supporting_rules.json`.
* `recommendations` reference actual products through `product_id`.
* `government_support` references actual support programmes through `support_id`.
* AI-generated explanations should not replace deterministic calculations or eligibility rules.

---

## 2. Exabytes Product — `/data/exabytes_products.json`

Contains the structured Exabytes product catalogue used by the recommendation engine.

```json
{
  "product_id": "string",
  "name": "string",
  "category": "cloud | website | productivity | crm | security | ai | other",
  "transformation_stage": "digitisation | digitalisation | digital_transformation | cybersecurity | ai",
  "target_business": [
    "retail",
    "f&b",
    "services"
  ],
  "problems_solved": [
    "string",
    "..."
  ],
  "benefits": [
    "string",
    "..."
  ],
  "prerequisites": [
    "string",
    "..."
  ],
  "pricing": "string | null",
  "grant_categories": [
    "string",
    "..."
  ],
  "source_url": "string",
  "source_date": "ISO 8601 date (when the information was captured)",
  "confidence": "high | medium | low"
}
```

### Design principle

The recommendation engine should reference `product_id` rather than hardcoding individual Exabytes products inside Python.

The product catalogue is therefore replaceable and maintainable without changing the core recommendation code.

---

## 3. Government Support — `/data/government_support.json`

Contains government grants, financing schemes, training support and other relevant forms of government assistance.

```json
{
  "support_id": "string",
  "programme": "string",
  "support_type": "grant | financing | training_support | tax_incentive | other",
  "source": "string (official source name)",
  "source_url": "string",
  "last_verified": "ISO 8601 date",
  "conditions": [
    "string",
    "..."
  ],
  "coverage": "string",
  "maximum_amount": "string | null",
  "minimum_amount": "string | null",
  "eligible_categories": [
    "string",
    "..."
  ],
  "eligibility_note": "Potentially eligible — eligibility is not guaranteed and must be confirmed against the current programme requirements.",
  "system_use": "string"
}
```

### Design principle

The system must distinguish between different types of government support.

For example:

* `grant`
* `financing`
* `training_support`
* `tax_incentive`
* `other`

The system must **never automatically describe financing or training support as a grant**.

Government support should be presented as:

> **Potentially eligible**

rather than as a guaranteed approval or funding outcome.

---

## 4. Supporting Rules — `/data/supporting_rules.json`

Contains deterministic business rules used by the assessment engine.

This includes:

* maturity scoring
* transformation priority
* lead scoring
* impact simulation
* adaptive assessment rules
* recommendation rules
* government-support rules
* boundaries between AI reasoning and deterministic calculations

Example structure:

```json
{
  "version": "1.0.0",
  "last_updated": "ISO 8601 date",

  "maturity_scoring": {
    "scale": {
      "min": 0,
      "max": 5
    },

    "dimensions": {
      "digital_presence": {
        "weight": 1.0
      },
      "productivity": {
        "weight": 1.0
      },
      "customer_management": {
        "weight": 1.2
      },
      "data_security": {
        "weight": 1.0
      },
      "ai_readiness": {
        "weight": 0.8
      }
    }
  },

  "priority_matrix": {
    "high_high": 1,
    "high_medium": 2,
    "high_low": 3,
    "medium_high": 2,
    "medium_medium": 3,
    "medium_low": 4,
    "low_high": 3,
    "low_medium": 4,
    "low_low": 5
  },

  "lead_scoring": {
    "weights": {
      "impact": 0.5,
      "urgency": 0.3,
      "digitisation_gap": 0.2
    }
  },

  "impact_simulation": {
    "weeks_per_year": 52,
    "formulas": {
      "annual_opportunity_cost": "hours_per_week * 52 * hourly_rate_assumption",
      "recovered_hours_per_year": "hours_per_week * 52 * automation_scenario_pct",
      "recovered_value_per_year": "recovered_hours_per_year * hourly_rate_assumption"
    }
  }
}
```

The complete rules are defined in `supporting_rules.json`.

---

## 5. Data Relationships

The main relationships between the data structures are:

```text
SME Assessment
      │
      ├── answers
      │
      ▼
Diagnosis
      │
      ├── pain point
      ├── root cause
      ├── evidence
      └── priority
      │
      ├───────────────┐
      ▼               ▼
Product Matcher   Government Matcher
      │               │
      ▼               ▼
product_id        support_id
      │               │
      ▼               ▼
Exabytes         Government
Products         Support
      │
      ▼
Final Transformation Plan
```

---

## 6. AI vs Deterministic Data

The system separates AI-generated reasoning from deterministic business calculations.

### AI / LLM responsibilities

The AI may:

* interpret free-text SME responses
* identify potential operational problems
* infer possible root causes
* identify missing information
* generate targeted follow-up questions
* explain the diagnosis
* explain why a product may be relevant
* generate the client-facing report
* generate the sales-facing brief

### Deterministic backend responsibilities

Python should calculate:

* maturity scores
* priority ranks
* annual opportunity cost
* recovered hours
* recovered value
* lead score
* rule-based eligibility checks
* product ID validation
* government support matching rules

This prevents the LLM from inventing financial calculations, scores or programme rules.

---

## 7. Data Validation

The backend should validate:

* `assessment_id` is a valid UUID.
* `created_at` is a valid ISO 8601 timestamp.
* maturity scores are between `0` and `5`.
* lead score is between `0` and `100`.
* automation percentage is between `0` and `1`.
* `product_id` exists in `exabytes_products.json`.
* `support_id` exists in `government_support.json`.
* priority ranks are generated from `supporting_rules.json`.
* government support is never displayed as guaranteed.
* financial impact is labelled as an estimate.

---

## 8. Source and Confidence Handling

`confidence`, `source_date`, and `last_verified` exist to prevent the system from presenting outdated or uncertain information as fact.

For product information:

```text
source_date → when the product information was captured
confidence  → confidence in the catalogue information
```

For government support:

```text
last_verified → when the programme information was last checked
```

If government support information is outdated or cannot be verified, the system should not present it as current.

### Core principle

> **JSON stores the facts and configurable rules. Python executes deterministic logic. The LLM handles interpretation, reasoning and explanation.**

