# 🚀 AI Horizon Challenge: SME Digital Transformation Consultant

> Empowering SMEs with intelligent, deterministic, and scalable digital transformation roadmaps.

## 💡 Inspiration
Small and Medium Enterprises (SMEs) are the backbone of the economy, yet many struggle to navigate the complexities of digital transformation. They often don't know where to start, what tools they need, or what government support is available to them. We wanted to build an intelligent consultant that not only acts as a friendly AI guide but grounds its advice in **hard math, determinism, and real-world ROI**.

## ⚙️ What it does
Our application is an AI-powered SME Digital Transformation Consultant that bridges the gap between conversational AI and rigid business logic. 
- **Adaptive Assessment:** It interviews SMEs dynamically, asking follow-up questions only when there's a genuine information gap.
- **Deterministic ROI & Scoring:** Instead of hallucinating numbers, the app uses a pure-Python deterministic engine to calculate digital maturity scores, labor opportunity costs, and sales lead scores based on a configurable ruleset.
- **Solution & Government Matching:** It matches SMEs to exact transformation products and flags potential government support programs (e.g., grants, tax incentives).
- **Sales Intelligence:** It acts as an internal tool for sales teams, instantly prioritizing hot leads and generating custom AI sales briefs.

## 🏗️ How we built it (Architecture)
We built the project with a strict separation of concerns between AI reasoning and deterministic math.

### Guiding Principle
> **The LLM reasons about the SME (understanding, gap detection, explanation).**
> **Deterministic code controls anything business-critical (scoring, ROI, eligibility).**

### Tech Stack
- **Frontend:** React + Tailwind CSS (Vite)
- **Backend:** FastAPI (Python)
- **AI Integration:** LangChain & Structured Outputs (OpenAI / Gemini)
- **Database:** SQLite with SQLModel / Pydantic for strict schema enforcement

### Folder Responsibilities
- **/frontend** - Handles the UI for the SME assessment flow, results report view, impact simulator, and the sales dashboard. Strictly presentation and state management.
- **/backend** - FastAPI application divided into:
  - **api/** - FastAPI route handlers.
  - **diagnosis/ & scoring/** - Deterministic engine for digital maturity scoring, ROI calculation, and lead scoring.
  - **solution_matching/** - Queries product and government data to match solutions deterministically.
  - **ai_chains/** - LangChain-based modules for AI reasoning (Analyst for gap detection, Strategist for generating explanations and sales briefs).
- **/data** - JSON configuration files acting as the single source of truth for government programs, products, and scoring rules.

## ⚠️ Challenges we ran into
- **Taming AI Hallucinations:** Large Language Models are great at talking but terrible at math. Our biggest challenge was stopping the LLM from inventing fake ROI numbers or promising non-existent government grants.
- **Strict Data Flow:** We had to carefully engineer LangChain `with_structured_output` chains to ensure the AI's diagnosis fed cleanly into our pure-Python mathematical scoring engine without breaking the JSON schema.

## 🏆 Accomplishments that we're proud of
- **The Analyst Loop:** We successfully built an adaptive "Information Gap" loop where the LLM stops asking questions as soon as it has enough evidence to diagnose the SME. 
- **100% Deterministic Engine:** All maturity scores, urgency levels, and lead scores are calculated natively in Python and strictly driven by our `supporting_rules.json` file. The AI only *explains* the math; it never *does* the math.
- **Enterprise-Grade UI & Sales Dashboard:** We designed and built a highly polished React frontend that faithfully represents an enterprise brand (Exabytes), featuring interactive ROI sliders, causal opportunity chains, maturity radar charts, and an intelligent internal sales pipeline dashboard.
- **The Strategist Chain:** We successfully implemented a secondary LLM pipeline that synthesizes the deterministic math into a compelling business narrative and AI sales brief.

## 📚 What we learned
We learned that the best AI applications don't use AI for everything. By constraining the LLM to roles it excels at (intent recognition, unstructured data parsing, and summarization) and offloading the rest to standard code, we created a vastly more reliable product.

## 🚀 What's next for the SME Consultant
- **Multi-Tenant Deployment:** Containerizing the frontend and backend with Docker for scalable cloud deployment.
- **CRM Integration:** Directly pushing hot leads and the AI Sales Brief into Salesforce or HubSpot.
- **Production Database:** Migrating from SQLite to PostgreSQL for scale.
