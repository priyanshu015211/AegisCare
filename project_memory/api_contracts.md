# AegisCare — API Contracts

Base URL: `http://localhost:8000/api/v1`
All endpoints require `Authorization: Bearer <jwt_token>` (Phase 5+)
All responses use the APIResponse envelope.

---

## Endpoints

### Health
GET /health
→ { status: "healthy" }

---

### Sessions
POST /api/v1/session/create
Body: SessionCreateRequest
→ SessionCreateResponse

GET /api/v1/session/{session_id}
→ SessionMemory

DELETE /api/v1/session/{session_id}
→ APIResponse

---

### Chat / Triage
POST /api/v1/chat
Body: ChatMessageRequest
→ ChatMessageResponse

Fields in ChatMessageResponse:
- session_id
- response (AI reply text)
- severity (green | yellow | red | critical)
- risk_score (0-100)
- escalation_triggered (bool)
- escalation_action (optional)
- follow_up_question (optional)

---

### Escalation
POST /api/v1/escalation/evaluate
Body: EscalationRequest
→ EscalationResponse

GET /api/v1/escalation/history/{session_id}
→ list[EscalationRecord]

---

### Appointments
POST /api/v1/appointment/book
Body: AppointmentRequest
→ AppointmentResponse

GET /api/v1/appointment/{appointment_id}
→ Appointment

PATCH /api/v1/appointment/{appointment_id}/status
Body: { status: AppointmentStatus }
→ APIResponse

---

### Reports
POST /api/v1/report/generate
Body: ReportRequest
→ ReportResponse

GET /api/v1/report/{session_id}
→ ReportResponse

---

### Hospital
GET /api/v1/hospital/load
→ list[HospitalLoadResponse]

GET /api/v1/hospital/{hospital_id}
→ Hospital

---

### Doctor
GET /api/v1/doctor/available
Query: specialty (optional), hospital_id (optional)
→ list[DoctorProfile]

GET /api/v1/doctor/{doctor_id}/availability
→ DoctorAvailability

---

## Standard Error Format
{
  "code": "error",
  "message": "Human-readable error description",
  "detail": "Technical detail for debugging",
  "timestamp": "2024-01-01T00:00:00Z"
}

## HTTP Status Codes Used
200 — Success
201 — Created
400 — Bad request (validation error)
401 — Unauthorized (missing/invalid token)
403 — Forbidden
404 — Not found
422 — Unprocessable entity (Pydantic validation)
429 — Rate limited
500 — Internal server error
