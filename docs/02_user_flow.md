# 02. User Flow

## High-level flow

```
Landing page
      ↓
SME starts assessment ("Start Digital Health Check")
      ↓
Basic company profile
  (industry, company size, current digital tools, main operational problems)
      ↓
Initial diagnosis (based on profile only)
      ↓
AI identifies information gaps
      ↓
Targeted follow-up question(s)
      ↓
Re-evaluate → repeat loop if a gap remains (max ~8–10 questions total)
      ↓
Final diagnosis (digital maturity + prioritised pain points)
      ↓
Impact / ROI simulator (interactive, assumption-visible)
      ↓
Digital maturity scorecard
      ↓
Recommended solutions (root cause → priority → solution → expected impact)
      ↓
3-phase transformation roadmap
      ↓
Output split:
  ├── SME-facing report (client view)
  └── Sales-facing brief (Exabytes sales dashboard)
```

## Step-by-step detail

### 1. Landing page
- Headline: "Discover what's holding your business back."
- CTA: **Start Digital Health Check**
- Sets expectation: ~5 minutes, personalised diagnosis, not a generic form.

### 2. Basic company profile (always asked, not adaptive)
- Industry
- Company size (employee count)
- Current digital tools in use (multi-select: website, WhatsApp, spreadsheets, CRM, POS, etc.)
- Main operational problems (open text or multi-select, kept broad)

### 3. Initial diagnosis
- Deterministic engine + LLM produce a first-pass hypothesis from the profile alone.
- Example: "You appear to have a customer-order management bottleneck."

### 4. Information gap detection (the adaptive loop)
- The AI Analyst chain asks: "What do I know? What's the biggest uncertainty that would change
  the diagnosis or the priority ranking?"
- If a gap is found → generate one targeted follow-up question.
  - Example: "How many hours per week does your team spend handling customer enquiries and orders?"
- If the answer changes the picture, a further clarifying question may be asked.
  - Example: "Do you lose enquiries/orders because multiple staff members handle WhatsApp separately?"
- Loop continues until either:
  - Confidence threshold is reached, or
  - Max question count (~8–10 total, including profile questions) is hit.

### 5. Final diagnosis
- Digital maturity scores across dimensions (see `06_scoring_logic.md`)
- Prioritised list of pain points with impact/urgency/priority

### 6. Impact Simulator
- Interactive slider(s) built from the SME's own stated numbers (e.g. hours/week on manual work)
- Shows current annual cost/opportunity, and a "what if you automate X%" scenario
- Assumptions are shown explicitly (hourly rate basis, hours/year conversion, etc.)

### 7. Digital Maturity scorecard
- Per-dimension score (Digital Presence, Productivity, Customer Management, Data & Security, AI Readiness)

### 8. Recommended solutions
- Each recommendation follows: observed problem → root cause → business impact → priority →
  recommended transformation → Exabytes solution → expected outcome

### 9. Transformation roadmap
- 3 phases: fix the top-priority bottleneck now, centralise/automate next, scale with AI later

### 10. Two outputs
- **SME report:** diagnosis, maturity, roadmap, recommended solutions, plain-language explanations
- **Sales brief:** lead priority score, primary problem, estimated impact, recommended approach,
  "why this lead is hot," and a short AI-generated talking-point brief

## Notes for implementation
- Keep the adaptive loop capped (max questions) to avoid runaway LLM conversations.
- Every branch of the flow should degrade gracefully if the SME skips a question (use "unknown"
  rather than blocking progress).
