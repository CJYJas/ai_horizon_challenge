# 03. Features — MVP vs Later

## MVP scope (build this for the hackathon)

### SME side
- [ ] Landing page with single CTA
- [ ] Adaptive assessment (profile + max ~8–10 questions total)
- [ ] AI diagnosis summary (top 3 pain areas, colour-coded severity)
- [ ] Impact Simulator (slider-based, current vs "automate X%" scenario, visible assumptions)
- [ ] Digital Maturity scorecard (5 dimensions)
- [ ] Transformation roadmap (3 phases, mapped to Exabytes solutions)
- [ ] SME-facing report view (on-screen; PDF export is a bonus, not the core deliverable)

### Sales side
- [ ] Sales dashboard: lead card per SME (priority score, primary problem, est. impact, maturity,
      recommended approach, "why this lead is hot," AI sales brief)
- [ ] Simple list/queue of leads sorted by priority score

### Backend / data
- [ ] Structured product catalog (`exabytes_products.json`) — 8–15 real, verified products
- [ ] Structured government/grant programme data (`government_programmes.json`) — small, verified set
- [ ] Deterministic scoring engine (maturity, impact/ROI, priority, lead score)
- [ ] Adaptive diagnosis loop (LangChain: Analyst chain → gap detection → follow-up → Strategist chain)
- [ ] Lightweight persistence for assessments (see `05_data_schema.md`)

## Explicitly NOT in MVP (avoid scope creep)

- ❌ Web scraper for every Malaysian grant/programme
- ❌ Large-scale RAG system over government or product documents
- ❌ 7–10 agent LLM pipeline (use 2–3 meaningful LLM stages instead)
- ❌ Real CRM integration
- ❌ Real payment processing
- ❌ Real sales automation / outbound messaging
- ❌ Massive, exhaustive Exabytes product database (start with 8–15 relevant products)
- ❌ Production-grade authentication system
- ❌ Complex AWS infrastructure (RDS "because Exabytes uses AWS" is not a justification on its own)
- ❌ 20–30 question static assessment

## Stretch goals (only if time remains)

- [ ] PDF export of SME report and/or sales brief
- [ ] Basic auth for the sales dashboard
- [ ] Persisting leads to a small hosted DB instead of local/SQLite
- [ ] A second demo scenario/persona to show the system generalises (see `09_demo_scenario.md`)

## Definition of done for the demo

A judge should be able to watch:
1. An SME profile go in,
2. See at least one adaptive follow-up question fire because of a genuine information gap,
3. See a diagnosis with a clear root cause (not just a checkbox result),
4. Interact with the Impact Simulator slider and see the numbers update,
5. See a roadmap with real Exabytes products attached,
6. Flip to the sales dashboard and see the same SME as a scored, explained lead.
