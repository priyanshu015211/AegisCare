"""
backend/db/database_service.py

AegisCare Database Service.
Wraps all Supabase operations with error handling and logging.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from backend.db.supabase_client import get_supabase_client
from backend.core.logging import get_logger

log = get_logger(__name__)


class DatabaseService:
    """
    Central database service for AegisCare.
    All Supabase table operations go through here.
    """

    def __init__(self):
        self.client = get_supabase_client()
        self.is_connected = self.client is not None
        if self.is_connected:
            log.info("DatabaseService initialised with Supabase connection")
        else:
            log.warning("DatabaseService running WITHOUT Supabase (no credentials)")

    # ------------------------------------------------------------------ #
    # Patient records                                                       #
    # ------------------------------------------------------------------ #

    async def save_patient(self, patient_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Insert or upsert a patient record."""
        if not self.is_connected:
            return None
        try:
            result = self.client.table("patients").upsert(patient_data).execute()
            log.info(f"Patient saved: {patient_data.get('patient_id', '?')}")
            return result.data[0] if result.data else None
        except Exception as e:
            log.error(f"Failed to save patient: {e}")
            return None

    async def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single patient by ID."""
        if not self.is_connected:
            return None
        try:
            result = (
                self.client.table("patients")
                .select("*")
                .eq("patient_id", patient_id)
                .single()
                .execute()
            )
            return result.data
        except Exception as e:
            log.error(f"Failed to fetch patient {patient_id}: {e}")
            return None

    async def list_patients(self) -> List[Dict[str, Any]]:
        """Return all patient records."""
        if not self.is_connected:
            return []
        try:
            result = self.client.table("patients").select("*").execute()
            return result.data or []
        except Exception as e:
            log.error(f"Failed to list patients: {e}")
            return []

    # ------------------------------------------------------------------ #
    # Triage sessions                                                       #
    # ------------------------------------------------------------------ #

    async def save_triage_session(self, session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Insert a new triage session row."""
        if not self.is_connected:
            return None
        try:
            result = self.client.table("triage_sessions").insert(session_data).execute()
            log.info(f"Triage session saved: {session_data.get('session_id', '?')}")
            return result.data[0] if result.data else None
        except Exception as e:
            log.error(f"Failed to save triage session: {e}")
            return None

    async def get_triage_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a triage session by ID."""
        if not self.is_connected:
            return None
        try:
            result = (
                self.client.table("triage_sessions")
                .select("*")
                .eq("session_id", session_id)
                .single()
                .execute()
            )
            return result.data
        except Exception as e:
            log.error(f"Failed to fetch session {session_id}: {e}")
            return None

    # ------------------------------------------------------------------ #
    # FIX Bug 2: Added missing methods called by patient_service.py        #
    # ------------------------------------------------------------------ #

    async def create_session(
        self, patient_id: str, symptoms: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new triage session for a patient.
        Returns the saved session dict (with session_id).
        Falls back to a local dict if Supabase is unavailable.
        """
        session_data = {
            "session_id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "symptoms": symptoms,
            "created_at": datetime.utcnow().isoformat(),
        }

        if not self.is_connected:
            log.warning("Supabase not connected — returning local session dict")
            return session_data

        saved = await self.save_triage_session(session_data)
        # If Supabase insert succeeded return it; otherwise return the local dict
        # so callers always get a usable session_id.
        return saved if saved else session_data

    async def add_symptom(self, session_id: str, symptom: str) -> bool:
        """
        Record an individual symptom linked to a triage session.
        Silently skips if Supabase is unavailable.
        """
        if not self.is_connected:
            return False
        try:
            data = {
                "session_id": session_id,
                "symptom": symptom,
                "recorded_at": datetime.utcnow().isoformat(),
            }
            self.client.table("session_symptoms").insert(data).execute()
            return True
        except Exception as e:
            log.error(f"Failed to add symptom to session {session_id}: {e}")
            return False

    async def update_patient_state(
        self, session_id: str, severity: str, risk_score: int
    ) -> bool:
        """
        Update severity and risk score on an existing triage session row.
        Silently skips if Supabase is unavailable.
        """
        if not self.is_connected:
            return False
        try:
            self.client.table("triage_sessions").update(
                {"severity": severity, "risk_score": risk_score}
            ).eq("session_id", session_id).execute()
            log.info(f"Patient state updated | session={session_id} severity={severity} risk={risk_score}")
            return True
        except Exception as e:
            log.error(f"Failed to update patient state for session {session_id}: {e}")
            return False

    # ------------------------------------------------------------------ #
    # Handoff reports                                                       #
    # ------------------------------------------------------------------ #

    async def save_handoff_report(
        self,
        session_id: str,
        patient_id: str,
        report_content: str,
    ) -> bool:
        """Save doctor handoff report to database."""
        if not self.is_connected:
            return False

        try:
            data = {
                "session_id": session_id,
                "patient_id": patient_id,
                "generated_at": datetime.utcnow().isoformat(),
                "report_markdown": report_content,
            }
            self.client.table("reports").insert(data).execute()
            log.info(f"Handoff report saved for session {session_id}")
            return True
        except Exception as e:
            log.error(f"Failed to save handoff report: {e}")
            return False


# ------------------------------------------------------------------ #
# FIX Bug 1: Singleton instance — importable as `db_service`          #
# ------------------------------------------------------------------ #
db_service = DatabaseService()
