# 🚀 AI Horizon Challenge: SME Digital Transformation Consultant

> Empowering SMEs with intelligent, deterministic, and scalable digital transformation roadmaps.

## 💡 Inspiration
Small and Medium Enterprises (SMEs) are the backbone of the economy, yet many struggle to navigate the complexities of digital transformation. They often don't know where to start, what tools they need, or what government support is available to them. We wanted to build an intelligent consultant that not only acts as a friendly AI guide but grounds its advice in **hard math, determinism, and real-world ROI**.

## ✨ Features
Our application bridges the gap between conversational AI and rigid business logic to deliver an end-to-end consulting experience:
- **Adaptive Diagnostic Interview:** A conversational AI flow that asks dynamic follow-up questions to uncover operational bottlenecks, without repeating questions or asking irrelevant details.
- **Deterministic Scoring Engine:** A pure-Python rules engine that evaluates digital maturity across 5 dimensions, calculates labor opportunity costs, and generates objective lead scores.
- **Automated Solution Matching:** Deterministically maps identified pain points to exact Exabytes products and matches SMEs with potential government support programs (e.g., grants, tax incentives).
- **Interactive Transformation Report:** A highly polished dashboard that visualizes the SME's digital maturity, highlights the biggest digital gap, and simulates ROI based on proposed automation.
- **Intelligent Sales CRM Dashboard:** An internal tool for sales teams that instantly prioritizes hot leads, extracts company info, and provides an AI-generated sales playbook with discovery questions, talk tracks, and objection handling.

## 🧠 Use of AI
The project employs Large Language Models (LLMs) strategically through two primary LangChain pipelines, constrained by strict Pydantic schemas:
1. **The AI Analyst Loop:** Instead of a rigid questionnaire, the AI Analyst analyzes incoming answers to detect "Information Gaps". It determines if it has enough evidence to form a root-cause hypothesis or if it needs to generate a targeted follow-up question.
2. **The AI Strategist Chain:** Once the deterministic engine calculates scores and matches products, the AI Strategist synthesizes this raw data into a human-readable transformation narrative. It generates custom explanations for low maturity scores and formulates a tailored sales brief to equip the sales team.

## 📈 Impact of AI on this Project
By integrating AI into the consulting and sales pipeline, the project achieves significant impact:
- **Scalable Discovery:** AI automates the time-consuming "discovery call" phase of B2B sales. SMEs receive immediate, consultative value at scale without requiring hours of human consultants' time.
- **Higher Sales Conversion:** The AI Strategist transforms raw assessment data into actionable sales playbooks. Sales reps enter calls equipped with contextual hooks, tailored objection responses, and exact ROI figures, drastically reducing prep time and increasing close rates.
- **Precision with Guardrails:** By offloading math and product matching to deterministic code, the AI's impact is focused purely on conversational extraction and storytelling. This completely eliminates the risk of AI hallucinating false pricing, ROI numbers, or non-existent grants, resulting in an enterprise-ready, trustable system.

## 🏗️ Architecture
We built the project with a strict separation of concerns between AI reasoning and deterministic math.

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
  - **ai_chains/** - LangChain-based modules for AI reasoning.
- **/data** - JSON configuration files acting as the single source of truth for government programs, products, and scoring rules.

## 🚀 What's next
- **Multi-Tenant Deployment:** Containerizing the frontend and backend with Docker for scalable cloud deployment.
- **CRM Integration:** Directly pushing hot leads and the AI Sales Brief into Salesforce or HubSpot.
- **Production Database:** Migrating from SQLite to PostgreSQL for scale.
