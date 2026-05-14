# AegisCare — API Contracts (Final)

**Base URL:** `http://localhost:8000/api/v1`

## Available Endpoints

### Health & System
- `GET /health`
- `GET /api/v1/system/status`

### Patient
- `POST /api/v1/patient/analyze`
- `POST /api/v1/patient/update`

### AI & Reasoning
- `POST /api/v1/ai/analyze`
- `POST /api/v1/ai/update-memory`
- `POST /api/v1/drift/analyze`

### Voice
- `POST /api/v1/voice/transcribe`
- `POST /api/v1/voice/respond`

### Coordination (Phase 6+)
- `POST /api/v1/appointment/book` *(Future)*
- `POST /api/v1/report/handoff` *(Future)*

## Response Format

**Success:**
```json
{
  "status": "success",
  "message": "...",
  "data": {},
  "timestamp": "..."
}
