"""
backend/core/constants.py

System-wide constants for AegisCare.
These values should NOT change at runtime.
Thresholds that administrators may need to tune belong in config.py instead.
"""

from enum import Enum


# ----------------------------------------------------------
# Severity Levels
# ----------------------------------------------------------

class SeverityLevel(str, Enum):
    """Patient severity classification."""
    GREEN = "green"       # Low risk — monitor
    YELLOW = "yellow"     # Medium risk — priority attention
    RED = "red"           # High risk — urgent intervention
    CRITICAL = "critical" # Immediate emergency — escalate now


# ----------------------------------------------------------
# Escalation Actions
# ----------------------------------------------------------

class EscalationAction(str, Enum):
    """Actions the system can trigger automatically."""
    MONITOR = "monitor"
    ALERT_DOCTOR = "alert_doctor"
    BOOK_APPOINTMENT = "book_appointment"
    DISPATCH_AMBULANCE = "dispatch_ambulance"
    INITIATE_VIDEO_CALL = "initiate_video_call"
    NOTIFY_EMERGENCY_CONTACT = "notify_emergency_contact"
    GENERATE_HANDOFF_REPORT = "generate_handoff_report"


# ----------------------------------------------------------
# Patient Memory
# ----------------------------------------------------------

class MemoryEventType(str, Enum):
    """Types of events recorded in the patient memory log."""
    SYMPTOM_REPORTED = "symptom_reported"
    SEVERITY_CHANGE = "severity_change"
    ESCALATION_TRIGGERED = "escalation_triggered"
    DOCTOR_ALERTED = "doctor_alerted"
    APPOINTMENT_BOOKED = "appointment_booked"
    VIDEO_CALL_STARTED = "video_call_started"
    REPORT_GENERATED = "report_generated"
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"


# ----------------------------------------------------------
# LLM Roles
# ----------------------------------------------------------

class LLMRole(str, Enum):
    """Roles for LLM prompt construction."""
    TRIAGE = "triage"           # Adaptive questioning
    REASONING = "reasoning"     # Differential analysis
    REPORT = "report"           # Doctor handoff report
    SUMMARY = "summary"         # Memory summarization


# ----------------------------------------------------------
# Doctor Availability
# ----------------------------------------------------------

class DoctorStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    ON_CALL = "on_call"
    OFFLINE = "offline"


# ----------------------------------------------------------
# Appointment Status
# ----------------------------------------------------------

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


# ----------------------------------------------------------
# Symptom Categories (Rule-based routing aid)
# ----------------------------------------------------------

RESPIRATORY_SYMPTOMS = frozenset({
    "cough", "shortness of breath", "difficulty breathing",
    "wheezing", "chest tightness", "rapid breathing",
    "breathlessness", "dyspnea",
})

CARDIAC_SYMPTOMS = frozenset({
    "chest pain", "palpitations", "heart racing", "irregular heartbeat",
    "chest pressure", "radiating arm pain", "jaw pain",
})

NEUROLOGICAL_SYMPTOMS = frozenset({
    "severe headache", "confusion", "loss of consciousness", "seizure",
    "sudden weakness", "facial drooping", "slurred speech", "dizziness",
})

CRITICAL_SYMPTOMS = frozenset({
    "not breathing", "no pulse", "unresponsive",
    "severe bleeding", "anaphylaxis",
}) | CARDIAC_SYMPTOMS | NEUROLOGICAL_SYMPTOMS


# ----------------------------------------------------------
# API Response Codes (internal use)
# ----------------------------------------------------------

class ResponseCode(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    ESCALATION_TRIGGERED = "escalation_triggered"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"


# ----------------------------------------------------------
# Token Budget (LLM optimization)
# ----------------------------------------------------------

MAX_CONTEXT_TOKENS = 800          # Max tokens sent per LLM call
SUMMARY_TRIGGER_TURNS = 15        # Summarize after this many turns
MAX_SYMPTOM_HISTORY_ITEMS = 10    # Max symptoms to keep in state
TRIAGE_QUESTION_LIMIT = 8         # Max clarifying questions before summary
