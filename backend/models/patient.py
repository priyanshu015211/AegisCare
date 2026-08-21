"""
backend/models/patient.py

Core Pydantic schemas for patient state, session, and symptom tracking.
These are the primary data contracts across the AegisCare system.

Design principles:
- All fields have sensible defaults (no required fields that break deserialization)
- Severity and risk are always kept in sync by the escalation engine (Phase 9)
- PatientState is the single source of truth sent to the LLM (token-optimized)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from backend.core.constants import (
    SeverityLevel,
    EscalationAction,
    MemoryEventType,
    AppointmentStatus,
)


# ----------------------------------------------------------
# Symptom Record
# ----------------------------------------------------------

class SymptomRecord(BaseModel):
    """A single symptom reported by the patient at a specific moment."""
    symptom: str
    reported_at: datetime = Field(default_factory=datetime.utcnow)
    duration: Optional[str] = None       # e.g. "2 days", "since this morning"
    severity_note: Optional[str] = None  # Patient-described severity
    category: Optional[str] = None       # respiratory | cardiac | neurological | general


# ----------------------------------------------------------
# Patient State (Token-Optimized LLM Context)
# ----------------------------------------------------------

class PatientState(BaseModel):
    """
    Compact structured representation of the patient's current condition.
    This is the ONLY context sent to the LLM — never the full conversation.

    Kept small deliberately. Max ~200 tokens when serialized.
    """
    patient_id: str
    session_id: str
    age: Optional[int] = None
    gender: Optional[str] = None         # e.g. "male", "female", "other"
    symptoms: list[str] = Field(default_factory=list)
    symptom_duration: Optional[str] = None
    severity: SeverityLevel = SeverityLevel.GREEN
    risk_score: int = Field(default=0, ge=0, le=100)
    escalation_triggered: bool = False
    current_action: Optional[EscalationAction] = None
    known_conditions: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


# ----------------------------------------------------------
# Memory Event (Audit Trail)
# ----------------------------------------------------------

class MemoryEvent(BaseModel):
    """A single logged event in the patient's session history."""
    event_type: MemoryEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    detail: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


# ----------------------------------------------------------
# Session Memory
# ----------------------------------------------------------

class SessionMemory(BaseModel):
    """
    Full in-memory record of a patient's session.
    Stored in Supabase and used for handoff report generation.
    """
    session_id: str
    patient_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    turn_count: int = 0
    symptom_history: list[SymptomRecord] = Field(default_factory=list)
    events: list[MemoryEvent] = Field(default_factory=list)
    summary: Optional[str] = None         # Rolling LLM-generated summary
    state: Optional[PatientState] = None  # Latest patient state snapshot


# ----------------------------------------------------------
# Patient Profile
# ----------------------------------------------------------

class PatientProfile(BaseModel):
    """Persisted patient profile stored in Supabase."""
    patient_id: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    known_conditions: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ----------------------------------------------------------
# Escalation Record
# ----------------------------------------------------------

class EscalationRecord(BaseModel):
    """Records an escalation event for audit and reporting."""
    escalation_id: str
    session_id: str
    patient_id: str
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    severity_at_trigger: SeverityLevel
    risk_score_at_trigger: int
    action_taken: EscalationAction
    symptoms_at_trigger: list[str] = Field(default_factory=list)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None


# ----------------------------------------------------------
# Appointment
# ----------------------------------------------------------

class Appointment(BaseModel):
    """A scheduled appointment between a patient and a doctor."""
    appointment_id: str
    patient_id: str
    doctor_id: str
    session_id: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = 15
    status: AppointmentStatus = AppointmentStatus.PENDING
    appointment_type: str = "in_person"  # in_person | video | phone
    agora_channel: Optional[str] = None  # Set for video appointments
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
