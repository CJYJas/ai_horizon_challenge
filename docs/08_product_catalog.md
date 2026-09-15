# 08. Product Catalog — Research Process

## Goal

Answer: **"What does Exabytes actually sell, and what business problems can each solution solve?"**
— then turn that into `/data/exabytes_products.json`.

## Rules for research

1. Go through the official Exabytes website (and only official sources) for each product.
2. Do **not** copy full marketing pages — extract the structured facts you actually need.
3. Do **not** invent capabilities, pricing, or eligibility that Exabytes doesn't explicitly state.
   If something is unclear, mark the field `null`/`"unknown"` and set `confidence: "low"`.
4. Start with **8–15 highly relevant products**, not the entire Exabytes catalog. Prioritise
   products that map cleanly onto common SME pain points: website presence, cloud/hosting,
   productivity/office tools, customer management, security, and any AI-related offerings.

## Per-product fields to collect

| Field | Example |
|---|---|
| Product | Product name |
| Category | Cloud / Website / Productivity / CRM / Security / AI |
| Target SME | Who it's for (industry, size) |
| Problems solved | Manual work, poor web presence, no backups, etc. |
| Benefits | What it improves, in plain language |
| Prerequisites | What the SME needs to have/do first |
| Pricing | Only if publicly stated — otherwise `null` |
| Source URL | Official Exabytes page |
| Last verified | Date you captured this |
| Confidence | high / medium / low |

## Record shape (matches `05_data_schema.md`)

```json
{
  "product_id": "string",
  "name": "string",
  "category": "cloud | website | productivity | crm | security | ai | other",
  "target_business": ["retail", "f&b", "services", "..."],
  "problems_solved": ["string", "..."],
  "benefits": ["string", "..."],
  "prerequisites": ["string", "..."],
  "pricing": "string | null",
  "grant_categories": ["string", "..."],
  "source_url": "string",
  "source_date": "ISO 8601 date",
  "confidence": "high | medium | low"
}
```

## Government / grant programme research (same discipline applies)

- Populate `government_programmes.json` with a **small number of verified initiatives** rather
  than scraping every Malaysian grant.
- Never hardcode a claim that a specific SME definitely qualifies — the system should only ever
  say **"potentially eligible"**, backed by:
  - the specific conditions matched,
  - the source,
  - the `last_verified` date.

```json
{
  "programme": "string",
  "source": "string",
  "source_url": "string",
  "last_verified": "ISO 8601 date",
  "conditions": ["string", "..."],
  "coverage": "string",
  "maximum_amount": "string | null",
  "eligible_categories": ["string", "..."]
}
```

## Production path (not built for MVP, just documented)

```
Government / Exabytes websites
       ↓
Document ingestion
       ↓
RAG / knowledge base
       ↓
Eligibility / matching engine   (still deterministic)
       ↓
LLM explanation
```

The MVP JSON files are intentionally structured so this later upgrade (JSON → DB → RAG) doesn't
require throwing away the MVP data model — only swapping the storage/retrieval layer.

## Checklist before building the JSON

- [ ] List of 8–15 candidate Exabytes products chosen
- [ ] Each product's official page opened and fields extracted (not guessed)
- [ ] Unknown fields explicitly marked, not left blank/silently omitted
- [ ] 2–5 government/grant programmes researched with the same discipline
- [ ] `exabytes_products.json` and `government_programmes.json` created in `/data`
