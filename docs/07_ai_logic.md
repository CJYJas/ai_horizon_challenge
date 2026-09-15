# 07. AI Logic (LLM responsibilities)

## Principle

The LLM is responsible for **understanding, reasoning, and explaining** — not for computing
numbers or deciding eligibility. See `06_scoring_logic.md` for everything that must stay
deterministic.

## LangChain pipeline (kept intentionally small — 2–3 meaningful stages)

```
                    USER ANSWERS
                         │
                         ▼
                ┌─────────────────┐
                │ Analyst Chain   │
                └────────┬────────┘
                         │
                         ▼
                Structured Diagnosis
                         │
                         ▼
              ┌─────────────────────┐
              │ Information Gap?    │
              └───────┬─────────────┘
                  YES  │       NO
                       │         │
                       ▼         │
                Follow-up Q      │
                       │          │
                       └──────┐   │
                              │   │
                              ▼   ▼
                         Diagnosis
                              │
                              ▼
                    Deterministic Engine   ← see 06_scoring_logic.md
                              │
              ┌───────────────┼──────────────┐
              ▼               ▼              ▼
          Maturity           ROI          Lead Score
                              │
                              ▼
                       Product Matcher       ← see 08_product_catalog.md
                              │
                              ▼
                       Strategist Chain
                              │
                  ┌───────────┴───────────┐
                  ▼                       ▼
             SME Report             Sales Brief
```

## Stage 1 — Analyst Chain

**Input:** company profile + all answers collected so far.

**Output (structured JSON, not free text):**
```json
{
  "hypotheses": ["string", "..."],
  "confidence": "low | medium | high",
  "information_gap": {
    "exists": true,
    "reason": "string — what's missing and why it matters",
    "follow_up_question": "string | null"
  }
}
```

**Responsibilities:**
- Interpret natural-language / multi-select answers into structured hypotheses about business
  problems.
- Decide whether there's a genuine information gap that would change the diagnosis or its priority.
- If yes, produce exactly one well-targeted follow-up question (not a checklist).
- Must respect the max-question cap enforced by the Assessment Engine — if the cap is reached,
  return `information_gap.exists = false` and proceed with best available confidence.

## Stage 2 — (loop) re-run Analyst Chain with the new answer

Same chain, same output shape, called again after each new answer until either:
- `information_gap.exists = false`, or
- Max question count is reached.

## Stage 3 — Strategist Chain

**Input:** final structured diagnosis + deterministic scoring output (maturity, impact, priority,
lead score) + shortlisted products from the Solution Matcher.

**Output (structured JSON):**
```json
{
  "pain_point_explanations": [
    { "problem": "string", "root_cause_explanation": "string", "why_it_matters": "string" }
  ],
  "roadmap_narrative": {
    "phase_1": "string",
    "phase_2": "string",
    "phase_3": "string"
  },
  "sme_report_summary": "string (plain language, non-technical)",
  "sales_brief": {
    "one_line_hook": "string",
    "why_this_lead_is_hot": ["string", "..."],
    "recommended_approach": "string"
  }
}
```

**Responsibilities:**
- Turn already-computed numbers into human-readable explanations.
- Generate the roadmap narrative and sales talking points.
- Must **never invent or alter** numbers that came from the deterministic engine — it should quote
  them as given.

## Guardrails

- Every LLM call should request structured JSON output (via LangChain structured output / tool
  calling) so the backend can validate and act on it — never parse free text for control flow.
- If the LLM output fails validation, fall back to a safe default (e.g. skip follow-up question,
  proceed with current confidence) rather than blocking the flow.
- The LLM must never state a grant eligibility as certain — only "potentially eligible" language,
  and only using data from `government_programmes.json`.
- The LLM must never claim a product capability that isn't present in `exabytes_products.json`.
