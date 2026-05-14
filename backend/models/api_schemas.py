"""
backend/models/api_schemas.py

Request and response schemas for all AegisCare API endpoints.
These are the public API contracts — keep them stable across phases.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field

from backend.core.constants import SeverityLevel, EscalationAction, ResponseCode


# ----------------------------------------------------------
# Generic API Response Envelope
# ----------------------------------------------------------

class APIResponse(BaseModel):
    """Standard response wrapper for all AegisCare API endpoints."""
    code: ResponseCode = ResponseCode.SUCCESS
    message: str = "OK"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class APIError(BaseModel):
    """Error response schema."""
    code: ResponseCode = ResponseCode.ERROR
    message: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ----------------------------------------------------------
# Chat / Triage
# ----------------------------------------------------------

class ChatMessageRequest(BaseModel):
    """Patient sends a message to the triage AI."""
    session_id: str
    patient_id: str
    message: str = Field(min_length=1, max_length=2000)
    voice_input: bool = False       # True if transcribed from audio


class ChatMessageResponse(BaseModel):
    """AI response to a patient message."""
    session_id: str
    response: str
    severity: SeverityLevel
    risk_score: int = Field(ge=0, le=100)
    escalation_triggered: bool = False
    escalation_action: Optional[EscalationAction] = None
    follow_up_question: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ----------------------------------------------------------
# Session
# ----------------------------------------------------------

class SessionCreateRequest(BaseModel):
    """Create a new triage session."""
    patient_id: str
    initial_complaint: Optional[str] = None


class SessionCreateResponse(BaseModel):
    """Returns the new session ID."""
    session_id: str
    patient_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ----------------------------------------------------------
# Escalation
# ----------------------------------------------------------

class EscalationRequest(BaseModel):
    """Manually trigger an escalation check."""
    session_id: str
    patient_id: str
    current_symptoms: list[str]
    risk_score: int = Field(ge=0, le=100)
    override_action: Optional[EscalationAction] = None


class EscalationResponse(BaseModel):
    """Result of escalation evaluation."""
    escalated: bool
    severity: SeverityLevel
    risk_score: int
    action: Optional[EscalationAction] = None
    reasoning: Optional[str] = None


# ----------------------------------------------------------
# Appointment
# ----------------------------------------------------------

class AppointmentRequest(BaseModel):
    """Request to book an appointment."""
    patient_id: str
    session_id: Optional[str] = None
    preferred_specialty: Optional[str] = None
    is_urgent: bool = False
    appointment_type: str = "in_person"


class AppointmentResponse(BaseModel):
    """Confirmed appointment details."""
    appointment_id: str
    doctor_name: str
    doctor_specialty: str
    scheduled_at: datetime
    appointment_type: str
    agora_channel: Optional[str] = None
    instructions: Optional[str] = None


# ----------------------------------------------------------
# Report
# ----------------------------------------------------------

class ReportRequest(BaseModel):
    """Request a doctor handoff report for a session."""
    session_id: str
    patient_id: str


class ReportResponse(BaseModel):
    """Generated doctor handoff report."""
    session_id: str
    patient_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    report_markdown: str
    severity_at_close: SeverityLevel
    risk_score_at_close: int


# ----------------------------------------------------------
# Hospital Load
# ----------------------------------------------------------

class HospitalLoadResponse(BaseModel):
    """Snapshot of hospital load for the dashboard."""
    hospital_id: str
    hospital_name: str
    load_percentage: float
    er_load_percentage: float
    ambulances_available: int
    is_accepting_emergency: bool
    updated_at: datetime
