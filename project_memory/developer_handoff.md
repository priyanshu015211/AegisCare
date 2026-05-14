# AegisCare — Developer Handoff

## Purpose of This File

This file contains everything a new developer (or AI model) needs
to continue development without access to previous conversation history.

---

## Project Summary

AegisCare is an AI-powered healthcare coordination platform.
Core innovation: Dynamic Emergency Drift Detection.
Tracks symptom progression in real time and escalates emergencies automatically.

Current state: Phase 1 complete (architecture and structure).
Next phase: Phase 2 (FastAPI backend implementation).

---

## Critical Design Decisions (Do Not Change Without Discussion)

1. Escalation is ALWAYS deterministic — never LLM-driven.
   Rule engine in backend/services/escalation/ owns all escalation logic.

2. LLMs receive PatientState JSON, never full conversation history.
   This is a token optimization and a reliability decision.

3. SeverityLevel has exactly 4 states: green, yellow, red, critical.
   UI maps these to specific colors defined in ui_guidelines.md.

4. All API responses use the APIResponse envelope (code, message, data, timestamp).
   Never return raw objects without this wrapper.

5. Session state is persisted in Supabase after every turn.
   The backend is stateless — never store session data in memory between requests.

---

## Key Files to Read First

1. project_memory/architecture.md — system overview and data flow
2. backend/core/config.py — all configurable values
3. backend/core/constants.py — all enums and thresholds
4. backend/models/patient.py — PatientState (the core data contract)
5. backend/models/api_schemas.py — all API request/response schemas
6. project_memory/ui_guidelines.md — before writing any frontend code

---

## Repository Root Structure

aegiscare/
├── backend/           Person 1 owns
├── frontend/          Person 2 owns
├── voice_pipeline/    Person 3 owns
├── project_memory/    All team members update
├── tests/             All team members contribute
├── docker/            Person 3 owns
└── scripts/           Person 3 owns

---

## Running the Project

See project_memory/env_setup.md for complete instructions.
Quick start:
  cp .env.example .env
  pip install -r requirements.txt
  uvicorn backend.main:app --reload
  streamlit run frontend/app.py
