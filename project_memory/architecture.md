# AegisCare — System Architecture

## Overview

AegisCare is a multi-tier AI healthcare coordination platform.
It separates concerns across three independently runnable services:
1. FastAPI backend (API, AI engine, business logic)
2. Streamlit frontend (patient UI, doctor dashboard)
3. Voice pipeline (STT/TTS processing)

All services communicate over HTTP. State is persisted in Supabase.

---

## Architecture Diagram

```
Patient / Browser
      │
      │  HTTPS
      ▼
┌─────────────────────────────┐
│    Streamlit Frontend        │  Port 8501
│  - Triage chat UI            │
│  - Live escalation indicator │
│  - Hospital dashboard        │
│  - Doctor command center     │
└────────────┬────────────────┘
             │  HTTP/REST
             ▼
┌─────────────────────────────┐
│    FastAPI Backend           │  Port 8000
│  - /api/v1/chat              │
│  - /api/v1/session           │
│  - /api/v1/escalation        │
│  - /api/v1/appointment       │
│  - /api/v1/report            │
│  - /api/v1/hospital          │
│  - /api/v1/doctor            │
└───┬─────────────┬────────────┘
    │             │
    │             │
    ▼             ▼
┌───────┐   ┌──────────────────┐
│ LLM   │   │   Supabase       │
│ APIs  │   │ - PostgreSQL DB  │
│       │   │ - Auth           │
│Gemini │   │ - Realtime       │
│GPT-4o │   └──────────────────┘
└───────┘
    
Voice Pipeline (separate process)
┌─────────────────────────────┐
│  Faster Whisper (STT)        │
│  XTTS-v2 / Piper (TTS)       │
│  PyAudio / SoundDevice       │
└─────────────────────────────┘
```

---

## Key Design Decisions

### 1. Deterministic Rule Engine for Escalation
The escalation system uses rule-based threshold evaluation, not LLM calls.
This guarantees consistent, auditable, fast escalation decisions.
LLMs are used ONLY for conversational reasoning and generating explanations.

### 2. Token-Optimized LLM Context
Only a compact PatientState JSON is sent to the LLM — never the full conversation.
PatientState is capped at ~200 tokens. Conversations are summarized after 15 turns.

### 3. Supabase as Single Source of Truth
All session state, patient profiles, escalation events, and appointments
are persisted in Supabase. The backend is stateless between requests.

### 4. Separate Voice Pipeline
Voice processing (STT/TTS) runs as a separate Python process to avoid
blocking the FastAPI event loop with CPU-intensive model inference.

### 5. Feature Flags via Environment
All thresholds and LLM model choices are configurable via .env.
No hardcoded values in business logic.

---

## Service Communication

| From       | To         | Protocol  | Auth         |
|------------|------------|-----------|--------------|
| Frontend   | Backend    | HTTP REST | JWT Bearer   |
| Backend    | Supabase   | HTTPS     | Service Role |
| Backend    | Gemini API | HTTPS     | API Key      |
| Backend    | Agora API  | HTTPS     | App ID + Cert|
| Voice      | Backend    | HTTP REST | Internal     |

---

## Data Flow: Patient Triage Session

1. Patient opens Streamlit UI, session created in Supabase
2. Patient types/speaks symptom
3. Frontend sends ChatMessageRequest to POST /api/v1/chat
4. Backend extracts symptoms, updates PatientState
5. Rule engine evaluates risk score
6. If escalation threshold met → trigger EscalationAction
7. LLM generates adaptive follow-up question (only if no escalation)
8. Response returned to frontend with severity level + risk score
9. Frontend updates severity indicator (GREEN/YELLOW/RED)
10. Steps 2-9 repeat. State updated each turn.
11. On session end → generate handoff report

---

## File Ownership Map (Team)

| Path                          | Owner    |
|-------------------------------|----------|
| backend/                      | Person 1 |
| backend/services/ai/          | Person 1 |
| backend/services/escalation/  | Person 1 |
| backend/api/routes/           | Person 1 |
| frontend/                     | Person 2 |
| frontend/components/          | Person 2 |
| frontend/pages/               | Person 2 |
| voice_pipeline/               | Person 3 |
| docker/                       | Person 3 |
| scripts/                      | Person 3 |
