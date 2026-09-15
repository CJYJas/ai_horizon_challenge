# 04. Architecture

## Guiding principle

> AI reasons about the SME (understanding, gap detection, explanation).
> Deterministic code controls anything business-critical (scoring, ROI, eligibility).

This split is the core defensibility story of the project — don't let it blur.

## System diagram

```
                    ┌───────────────┐
                    │ React Frontend│
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │ FastAPI       │
                    └───────┬───────┘
                            ↓
                 ┌─────────────────────┐
                 │ Assessment Engine   │
                 └─────────┬───────────┘
                           ↓
                 ┌─────────────────────┐
                 │ AI Analyst          │  (LLM)
                 │ "What do I know?"   │
                 └─────────┬───────────┘
                           ↓
                 ┌─────────────────────┐
                 │ Information Gap     │  (LLM)
                 │ Detection           │
                 └─────────┬───────────┘
                           ↓
                 ┌─────────────────────┐
                 │ Adaptive Question   │  (LLM)
                 └─────────┬───────────┘
                           ↓
                    [LOOP / RECHECK]
                           │
                    enough evidence?
                     ↙           ↘
                   NO             YES
                   ↑               ↓
             Ask again      Diagnosis Engine
                                   ↓
                         ┌──────────────────┐
                         │ Deterministic    │  (Python)
                         │ Scoring + ROI    │
                         └────────┬─────────┘
                                  ↓
                         ┌──────────────────┐
                         │ Solution Matcher │  (Python, queries product JSON)
                         └────────┬─────────┘
                                  ↓
                         ┌──────────────────┐
                         │ AI Strategist    │  (LLM)
                         └────────┬─────────┘
                                  ↓
                       ┌──────────────────────┐
                       │ Client + Sales View  │
                       └──────────────────────┘
```

## Component responsibilities

### Frontend — React + Tailwind
- Landing page, assessment flow, results/report view, Impact Simulator (interactive slider),
  sales dashboard.
- No business logic beyond form state and API calls.

### Backend — FastAPI
- Exposes endpoints for: starting an assessment, submitting answers, fetching diagnosis/report,
  fetching sales dashboard data.
- Orchestrates the call order between the deterministic engine and the LLM chains.

### Assessment Engine (Python, deterministic)
- Tracks assessment state (which questions asked, answers so far, loop count).
- Enforces the max-question cap.

### AI Analyst / Gap Detection / Adaptive Question chains (LangChain + LLM)
- Given current structured answers, produce: (a) a structured partial diagnosis, and
  (b) either "sufficient evidence" or one targeted follow-up question.
- Output must be **structured JSON**, not free text, so the backend can act on it deterministically.

### Diagnosis Engine (Python, deterministic)
- Digital maturity scoring (see `06_scoring_logic.md`)
- Impact/ROI calculation
- Priority scoring (impact × urgency)
- Lead scoring (for sales dashboard)

### Solution Matcher (Python)
- Queries `exabytes_products.json` using structured diagnosis output (problems, category, business size)
  to shortlist candidate products. No LLM involved in this step — it's rule/filter based.

### AI Strategist chain (LangChain + LLM)
- Takes the deterministic diagnosis + shortlisted products and produces:
  - Human-readable explanation of the root cause and recommendation
  - The 3-phase roadmap narrative
  - The sales brief talking points
- Does **not** invent numbers — it explains numbers that were already computed deterministically.

### Data layer
- MVP: JSON files for product catalog and grant programmes (`/data/*.json`), lightweight DB
  (e.g. SQLite/Postgres) for assessment records.
- Production path (documented, not built for MVP): S3 for source documents → structured DB →
  RAG/vector search for grant and product knowledge, still gated behind the same deterministic
  eligibility/scoring engine.

## Why not more agents

A 7–10 agent pipeline is not inherently better — it adds latency, cost, and failure surface for a
hackathon demo. Two to three well-scoped LLM stages (Analyst → Strategist, with gap-detection as
part of the Analyst stage) is enough to tell the "adaptive diagnosis" story clearly.

## Why not AWS RDS by default

Only reach for AWS pieces (RDS, S3, etc.) if they solve a real need in the MVP. If used, be able to
explain the scalability path (S3 → FastAPI → DB) rather than justifying it as "Exabytes uses AWS."
