"""
backend/ai/memory/patient_memory.py

In-session patient memory store.

Tracks the symptoms, severity, risk score, and conversation state for a
single triage session.  Keyed on (patient_id:session_id) by the caller
in ai.py so concurrent sessions for the same patient never collide.

Bug 3 fix:
    All three datetime.utcnow() calls replaced with datetime.now(timezone.utc).
    datetime.utcnow() is deprecated since Python 3.12 and will be removed in
    a future release.  The replacement produces a timezone-aware datetime
    object (UTC), whereas utcnow() produced a naive one — this also fixes
    potential serialisation surprises when the datetime is sent as JSON.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.core.logging import get_logger

log = get_logger(__name__)


class PatientMemory:
    """
    Lightweight in-memory state for one triage session.

    NOTE: This object lives only for the lifetime of the Python process.
    It is not persisted between requests or restarts.  For cross-request
    continuity, the caller should pass the same memory_key so the same
    instance is reused within a process, or use the Supabase session record
    as the source of truth (Phase 4+).
    """

    def __init__(self, patient_id: str) -> None:
        self.patient_id: str = patient_id
        self.symptoms: List[str] = []
        self.severity: str = "low"
        self.risk_score: int = 0
        self.confidence: float = 0.0
        self.conversation_summary: str = ""
        self.escalation_history: List[Dict[str, Any]] = []
        # Bug 3 fix: timezone-aware UTC timestamp
        self.last_updated: datetime = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def add_symptom(self, symptom: str) -> None:
        """Add a symptom if it is not already present (case-insensitive)."""
        normalised = symptom.lower().strip()
        if normalised and normalised not in [s.lower() for s in self.symptoms]:
            self.symptoms.append(normalised)
            # Bug 3 fix: timezone-aware UTC timestamp
            self.last_updated = datetime.now(timezone.utc)

    def update_risk(
        self,
        risk_score: int,
        severity: str,
        confidence: float,
    ) -> None:
        """Record a new risk assessment result."""
        self.risk_score = risk_score
        self.severity = severity
        self.confidence = confidence
        # Bug 3 fix: timezone-aware UTC timestamp
        self.last_updated = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        """Return the current session state as a plain dict."""
        return {
            "patient_id": self.patient_id,
            "symptoms": self.symptoms,
            "previous_symptoms": self.symptoms,   # alias used by ai_engine
            "severity": self.severity,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "conversation_summary": self.conversation_summary,
            "escalation_history": self.escalation_history,
            "last_updated": self.last_updated.isoformat(),
        }
