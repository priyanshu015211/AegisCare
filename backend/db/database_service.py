"""
backend/db/database_service.py

AegisCare Database Service.
Wraps all Supabase operations with error handling and logging.

FIX Bug 4: Removed the module-level `db_service = DatabaseService()` singleton.
That line ran at import time, which meant any Supabase misconfiguration or
network blip during startup would raise an exception and crash the entire
FastAPI process before it could serve a single request.

Instead, `get_db_service()` is a lazy factory:
- It creates the DatabaseService on first call, not at import time.
- FastAPI's Depends() calls it per-request but the instance is cached via
  a module-level variable so only one instance is ever created.
- Any file that previously did `from backend.db.database_service import db_service`
  must switch to `from backend.db.database_service import get_db_service`
  and call get_db_service() to obtain the instance.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from backend.db.supabase_client import get_supabase_client
from backend.core.logging import get_logger

log = get_logger(__name__)

# Module-level cache — populated on first call to get_db_service(), not at import.
_db_service_instance: Optional["DatabaseService"] = None


def get_db_service() -> "DatabaseService":
    """
    Lazy factory for DatabaseService.

    Returns the same instance on every call (singleton), but defers
    creation until the first actual call so import-time crashes are
    impossible even when Supabase credentials are absent or the
    network is unavailable at startup.
    """
    global _db_service_instance
    if _db_service_instance is None:
        _db_service_instance = DatabaseService()
    return _db_service_instance


class DatabaseService:
    """
    Central database service for AegisCare.
    All Supabase table operations go through here.

    Do not instantiate directly — use get_db_service() instead.
    """

    def __init__(self):
        # Connection is attempted here, but this constructor is only called
        # from get_db_service() on first use, never at module import time.
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
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if not self.is_connected:
            log.warning("Supabase not connected — returning local session dict")
            return session_data

        saved = await self.save_triage_session(session_data)
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
                "recorded_at": datetime.now(timezone.utc).isoformat(),
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
            log.info(
                f"Patient state updated | session={session_id} "
                f"severity={severity} risk={risk_score}"
            )
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
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "report_markdown": report_content,
            }
            self.client.table("reports").insert(data).execute()
            log.info(f"Handoff report saved for session {session_id}")
            return True
        except Exception as e:
            log.error(f"Failed to save handoff report: {e}")
            return False
