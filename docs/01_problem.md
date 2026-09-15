# 01. Problem Statement

## What Exabytes wants to solve

Exabytes sells a wide range of digital solutions to SMEs (cloud, website, productivity, CRM,
security, AI tools, etc.), but most SMEs don't know:

- What digital problems they actually have
- Which problems are costing them the most (time / money / opportunity)
- Which Exabytes product(s) would actually fix the *root cause*, not just a symptom

Today this diagnosis work is done manually by a salesperson or consultant. That doesn't scale,
is inconsistent, and often turns into "product pushing" rather than genuine problem-solving.

## Target user

**Primary:** Malaysian SMEs (micro to small businesses, roughly 1–50 employees) across sectors
such as retail, F&B, services, and light manufacturing, who have low-to-medium digital maturity.

**Secondary:** Exabytes sales team, who receive the output of the diagnosis as a qualified,
prioritised lead with a ready-made sales narrative.

## Why current digital consultation is inefficient

- Manual discovery calls take time and don't scale across thousands of SMEs.
- Generic questionnaires ("Do you have a website? Do you use a CRM?") collect checkbox answers,
  not real operational pain points.
- Recommendations are often reactive ("no CRM → sell CRM") instead of diagnostic
  ("20 hrs/week manually handling enquiries → fragmented customer management → CRM + automation").
- SMEs can't easily see the financial impact of *not* fixing a problem, so urgency isn't clear.
- Sales teams don't get enough context to open a conversation with anything beyond a generic pitch.

## Our proposed solution

An **AI-powered SME Digital Transformation Consultant** that:

1. Runs an **adaptive diagnosis** (not a static 5-question form) that asks targeted follow-up
   questions only when there's a real information gap.
2. Converts answers into a **quantified diagnosis**: root cause → business impact → priority.
3. Simulates the **financial/time impact** of the SME's current pain points (Impact Simulator),
   with visible assumptions — not an invented "AI shock number."
4. Produces a **prioritised, phased transformation roadmap** mapped to real Exabytes solutions.
5. Generates a **sales-ready brief** for the Exabytes sales team, not just a PDF for the SME.

### What makes this different from "a form + an LLM + a PDF"

The core value is the **diagnosis and reasoning layer**, not the document generation. Deterministic
business logic (scoring, ROI, eligibility) is handled by regular code; the AI is responsible for
understanding language, spotting information gaps, asking good follow-up questions, and explaining
the "why" behind each recommendation. See `07_ai_logic.md` and `06_scoring_logic.md` for the split.

## One-line pitch

> "SMEs don't know what digital technology they need. Our system acts as an AI digital consultant
> that diagnoses the SME's real operational bottlenecks, quantifies the impact, and turns that into
> a prioritised, sales-ready transformation plan for Exabytes."
