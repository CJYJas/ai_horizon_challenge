# 09. Demo Scenario

## Primary demo persona

**ABC Enterprise** — Retail, 8 employees.

### Profile answers
- Industry: Retail
- Employee count: 8
- Current digital tools: WhatsApp, spreadsheets (no website, no CRM)
- Main operational problems: "Hard to keep track of customer orders"

### Adaptive loop (what should happen live in the demo)

1. Initial diagnosis (from profile alone):
   > "You appear to have a customer-order management bottleneck. I need one more piece of information."
2. Follow-up question #1:
   > "How many hours per week does your team spend handling customer enquiries and orders?"
   - Answer: **20 hrs/week**
3. Follow-up question #2 (triggered because the first answer raised a new, higher-value question):
   > "Do you lose enquiries/orders because multiple staff members handle WhatsApp separately?"
   - Answer: **Yes**
4. Loop ends — enough evidence, diagnosis finalised.

### Expected diagnosis output

| Observed problem | Root cause | Business impact | Priority |
|---|---|---|---|
| 20 hrs/week manually managing customer enquiries | Customer interactions fragmented across WhatsApp + spreadsheets + multiple staff | ~RM26,000/year labour opportunity | 🔴 HIGH |
| No business email / basic web presence | Low digital presence | Medium | 🟡 MEDIUM |
| No website analytics | Limited visibility into customer behaviour | Low | 🟢 LOW |

### Digital Maturity scorecard (expected demo values)

| Dimension | Score |
|---|---|
| Digital Presence | 2/5 |
| Productivity | 2/5 |
| Customer Management | 1/5 |
| Data & Security | 2/5 |
| AI Readiness | 1/5 |

### Impact Simulator (interactive part of the demo)

- Slider: "How much time does your team spend handling customer enquiries?" (5–30 hrs, default 20)
- Current: 20 hrs/week → 1,040 hrs/year → **RM20,800/year** estimated labour opportunity
- Move slider to simulate "automate 50%": recovered **520 hrs/year** → **RM10,400/year**
- Assumptions (hourly rate basis) shown on screen at all times.

### Transformation roadmap (expected narrative)

```
NOW
│
├── Fix customer enquiry management
│
▼
PHASE 1 — Centralise customer interactions
▼
PHASE 2 — Automate repetitive workflows
▼
PHASE 3 — Use AI to scale customer operations
```

Each phase should list the actual matched Exabytes product(s) from `exabytes_products.json`.

### Sales dashboard card (expected demo output)

```
NEW LEAD
ABC Enterprise — Retail • 8 employees

LEAD PRIORITY: 92 / 100 🔴 HOT

PRIMARY PROBLEM: Manual customer enquiries — 20 hrs/week
EST. IMPACT: RM20,800/year

DIGITAL MATURITY: 2.1 / 5

RECOMMENDED APPROACH:
1. Customer management
2. Automation
3. Business productivity

WHY THIS LEAD IS HOT:
✓ High operational pain
✓ High urgency
✓ Identified budget concern
✓ Clear digitalisation opportunity

AI SALES BRIEF:
"Lead with the time-saving problem, not technical features."
```

## Secondary demo persona (stretch goal, if time allows)

Add a second, different persona (e.g. a small F&B business with a different pain point — perhaps
inventory/stock tracking rather than customer enquiries) to show the diagnosis engine generalises
and doesn't just replay a scripted path. Define its profile, expected loop, and expected outputs
here once chosen.

## Demo script checklist

- [ ] Walk through the landing page and CTA
- [ ] Enter ABC Enterprise's profile live
- [ ] Show at least one adaptive follow-up question firing in real time
- [ ] Show the diagnosis with root cause (not just a checkbox result)
- [ ] Move the Impact Simulator slider and show numbers update live
- [ ] Show the maturity scorecard and roadmap with real Exabytes products attached
- [ ] Switch to the sales dashboard and show the same SME as a scored, explained lead
- [ ] Close with the one-line pitch from `01_problem.md`
