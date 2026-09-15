# 06. Scoring Logic

All scoring and financial calculations in this document are **deterministic** and must be implemented in plain Python.

The calculations are driven by `/data/supporting_rules.json` wherever possible.

The LLM **does not calculate, modify or override numerical results**. It may only explain the results after the deterministic engine has produced them.

---

## 1. Digital Maturity Score

The SME is assessed across five dimensions, each scored from **0–5**:

| Dimension           | Signals Used                                                                        |
| ------------------- | ----------------------------------------------------------------------------------- |
| Digital Presence    | Website, social media presence, online visibility tools                             |
| Productivity        | Spreadsheets vs software, manual vs automated workflows                             |
| Customer Management | CRM usage, channel fragmentation across WhatsApp/email/spreadsheets                 |
| Data & Security     | Backups, cloud storage, security practices                                          |
| AI Readiness        | Existing automation, data structure, staff digital literacy and technology adoption |

Each dimension is calculated using deterministic scoring rules stored in `/data/supporting_rules.json`.

Example rule structure:

* No website → low digital presence score
* Website exists but is poorly maintained → developing score
* Active website with analytics and digital channels → strong score
* Manual spreadsheet-heavy workflow → lower productivity score
* Automated workflow using dedicated software → higher productivity score

The exact scoring thresholds should be stored in `supporting_rules.json` so they can be tuned without changing Python code.

### Weighted maturity score

Each dimension has a configurable weight:

```text
digital_presence      = 1.0
productivity          = 1.0
customer_management   = 1.2
data_security         = 1.0
ai_readiness          = 0.8
```

The weighted overall maturity score is:

```text
overall_maturity =
    Σ(dimension_score × dimension_weight)
    ÷
    Σ(dimension_weight)
```

The five individual dimension scores remain available for the SME dashboard.

---

## 2. Impact / ROI Calculation

The Impact Simulator uses inputs provided by the SME.

The system must **not invent the number of hours spent on a problem**.

### Annual opportunity cost

```text
hours_per_year =
    hours_per_week × 52

annual_opportunity_cost =
    hours_per_year × hourly_rate_assumption
```

Where:

* `hours_per_week` comes from the SME's answer.
* `52` is defined in `supporting_rules.json` as `weeks_per_year`.
* `hourly_rate_assumption` is a visible and editable assumption.

The hourly rate should be clearly displayed to the user.

Example:

```text
10 hours/week
× 52
= 520 hours/year

520 hours
× RM25/hour
= RM13,000 estimated annual opportunity cost
```

### Automation scenario

The user can adjust the estimated automation percentage through a UI slider.

```text
recovered_hours_per_year =
    hours_per_year × automation_scenario_pct

recovered_value_per_year =
    recovered_hours_per_year × hourly_rate_assumption
```

For example:

```text
Automation scenario = 50%

520 hours/year × 50%
= 260 recovered hours/year
```

Results must always be presented as **estimates**.

The UI must show the assumptions used in the calculation.

The system must never claim that the SME will definitely save or recover the calculated amount.

---

## 3. Priority Scoring

Each diagnosed pain point receives two deterministic classifications:

### Impact

Impact is classified as:

```text
low
medium
high
```

Impact is determined using configurable rules based on factors such as:

* Annual opportunity cost
* Estimated recoverable value
* Number of affected business areas
* Number of maturity dimensions affected

The exact thresholds should be stored in `/data/supporting_rules.json`.

### Urgency

Urgency is classified as:

```text
low
medium
high
```

Urgency is derived from explicit signals in the SME's responses.

Examples:

* "Would be nice to have" → low urgency
* "Causes problems every month" → medium urgency
* "Currently losing customers / disrupting operations" → high urgency

The AI may identify the relevant evidence from the SME's answers, but the final urgency classification must be produced using deterministic rules.

### Priority matrix

Priority is calculated by looking up the combination of impact and urgency in the matrix stored in `supporting_rules.json`.

```text
                 URGENCY
              Low  Medium  High

Impact High     3      2      1
Impact Medium   4      3      2
Impact Low      5      4      3
```

Where:

```text
1 = Highest priority
5 = Lowest priority
```

The system may additionally map priority to a display status:

```text
Priority 1–2 → High
Priority 3   → Medium
Priority 4–5 → Low
```

Colour presentation is a **frontend concern**, not a scoring rule.

Recommended display:

```text
High   → 🔴
Medium → 🟡
Low    → 🟢
```

---

## 4. Lead Score

The lead score ranges from **0–100** and is used only for sales prioritisation.

It combines:

1. Impact magnitude
2. Urgency
3. Digitisation gap

The weights are stored in `supporting_rules.json`:

```text
impact            = 0.5
urgency           = 0.3
digitisation_gap  = 0.2
```

The calculation is:

```text
lead_score =
    (impact_weight × impact_norm)
    +
    (urgency_weight × urgency_norm)
    +
    (gap_weight × digitisation_gap_norm)
```

### Normalisation

The three inputs must first be converted to a **0–100 scale**.

The normalisation thresholds must be explicitly defined in `supporting_rules.json`.

For example:

```text
impact_norm
→ converts annual opportunity cost into 0–100

urgency_norm
→ low    = 33
→ medium = 66
→ high   = 100

digitisation_gap_norm
→ converts the maturity gap into 0–100
```

The exact impact and maturity-gap thresholds must come from `supporting_rules.json`.

The Python engine performs the calculation.

The LLM must never generate the final lead score.

### Lead score reasons

The system should generate 2–4 short reasons explaining the score.

Examples:

```text
"High operational impact"
"High urgency"
"Large productivity gap"
"Significant manual workload"
```

These reasons should be based on the deterministic results and evidence already stored in the assessment.

---

## 5. Government Support Matching

Government support is stored separately in:

```text
/data/government_support.json
```

The system must never automatically state:

> "You qualify."

Instead, it should state:

> **Potentially eligible**

The system should display:

* Programme name
* Support type
* Matching transformation category
* Matching conditions
* Official source
* Last verified date
* Eligibility note

Government support can include different types of assistance:

```text
grant
financing
training_support
tax_incentive
other
```

The system must not describe financing or training support as a grant.

Eligibility matching should be rule-based where possible.

The system must not guarantee:

* approval
* eligibility
* funding
* reimbursement
* funding amount

If programme information is outdated or cannot be verified, the system should not present it as current.

---

## 6. Recommendation Priority

Product recommendations are generated only after the diagnosis and scoring stages.

The recommendation chain is:

```text
SME Answers
     ↓
Evidence
     ↓
Problem
     ↓
Root Cause
     ↓
Business Impact
     ↓
Urgency
     ↓
Priority
     ↓
Relevant Transformation
     ↓
Exabytes Product
```

The product matcher uses `/data/exabytes_products.json`.

The system should match products primarily against:

1. Root cause
2. Problems solved
3. Business context
4. Current digital tools
5. Industry

The system should recommend a relevant transformation rather than simply recommending products based on industry.

Each recommendation must contain:

```text
product_id
linked_pain_point
reason
expected_outcome
```

---

## 7. AI Boundaries

The deterministic engine and LLM have different responsibilities.

### Python / Deterministic Engine

Python is responsible for:

* Maturity scoring
* Weighted maturity calculation
* Impact classification
* Urgency classification
* Priority ranking
* Annual opportunity cost
* Recovered hours
* Recovered value
* Lead score
* Normalisation
* Rule-based government support matching
* Product ID validation

### LLM

The LLM is responsible for:

* Understanding SME free-text responses
* Identifying potential problems
* Identifying possible root causes
* Identifying missing information
* Generating targeted follow-up questions
* Explaining deterministic results
* Generating recommendation explanations
* Generating the client report
* Generating the sales brief

The LLM must not override deterministic results.

---

## 8. Testing

All deterministic calculations must be unit-testable without an LLM.

Tests should cover:

### Maturity

```text
Given known profile + answers
→ expected dimension scores
→ expected weighted maturity score
```

### Impact

```text
10 hours/week
RM25/hour
→ 520 hours/year
→ RM13,000 annual opportunity cost
```

### Automation

```text
10 hours/week
50% automation
→ 260 recovered hours/year
→ RM6,500 recovered value/year
```

### Priority

Test all nine impact × urgency combinations:

```text
high × high       → 1
high × medium     → 2
high × low        → 3

medium × high     → 2
medium × medium   → 3
medium × low      → 4

low × high        → 3
low × medium      → 4
low × low         → 5
```

### Lead Score

Test:

* Lowest possible score
* Highest possible score
* High-impact/high-urgency case
* Large digitisation gap case
* Normal case

### Government Support

Test that:

* Matching programmes are labelled `potentially_eligible`
* Unmatched programmes are not recommended
* Missing verification dates are rejected
* The system never produces a guaranteed eligibility statement

---

## 9. Source of Truth

The following files are the source of truth:

```text
/data/exabytes_products.json
    → Exabytes product information

/data/government_support.json
    → Government support information

/data/supporting_rules.json
    → Scoring, calculation and matching rules
```

Python reads these files at runtime.

Business logic should not be duplicated in hardcoded `if/else` branches.

The architecture should allow the rules and catalogue to be updated without rewriting the core application.

---

## Core Principle

> **The LLM reasons about the SME. Python decides the numbers.**
>
> **The LLM explains the result. It does not create the result.**
