"""
backend/db/database_service.py

AegisCare Database Service.
Wraps all Supabase operations with error handling and logging.
"""

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
    # Handoff reports                                                        #
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
