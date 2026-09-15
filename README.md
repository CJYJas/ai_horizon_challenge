# AI Horizon Challenge Project

## Architecture & Folder Responsibilities

This project implements an AI-powered SME Digital Transformation Consultant. It separates concerns between the AI components (which handle reasoning and language understanding) and deterministic logic (which handles business-critical logic such as scoring, ROI, and product eligibility).

### System Overview

- **/frontend** - React + Tailwind application. 
  - Contains the UI for the SME assessment flow, results report view, impact simulator, and the sales dashboard. 
  - Responsibility: Strictly presentation and state management. No business logic beyond form state and API calls.
  
- **/backend** - FastAPI application.
  - Exposes endpoints to orchestrate the assessment, process diagnosis, and generate sales dashboard data.
  - Divided into several logical components:
    - **api/** - FastAPI route handlers exposing the endpoints.
    - **assessment/** - Manages the assessment state (questions asked, answers, loop count).
    - **diagnosis/** - Deterministic engine for digital maturity scoring, ROI calculation, and lead scoring.
    - **scoring/** - Core deterministic scoring logic (can be combined with diagnosis).
    - **solution_matching/** - Queries product and government data to match solutions deterministically based on diagnosis.
    - **ai_chains/** - LangChain-based modules for AI reasoning (Analyst for gap detection, Strategist for generating explanations and sales briefs).

### Guiding Principle

> AI reasons about the SME (understanding, gap detection, explanation).
> Deterministic code controls anything business-critical (scoring, ROI, eligibility).
