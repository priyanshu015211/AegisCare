# AegisCare — System Architecture (Final)

## Layers

- **Frontend**: Streamlit (Dashboard, Triage, Coordination, Analytics)
- **Backend**: FastAPI
  - API Layer (`/api/v1`)
  - Service Layer
  - AI Layer (`ai/`)
  - Voice Layer (`voice/`)
  - Coordination Layer
- **AI**: Gemini + Rule-based engines (Drift, Risk, Escalation)
- **Voice**: Faster Whisper (STT) + XTTS (TTS)
- **Deployment**: Docker + docker-compose

## Key Design Decisions
- Clean separation between routes, services, and AI logic
- Structured Patient Memory (JSON-based)
- Rule-based + AI hybrid for escalation
- Placeholder architecture for voice and video (ready for real integration)
