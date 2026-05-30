"""
backend/db/database_service.py

AegisCare Database Service.
Wraps all Supabase operations with error handling and logging.

Key fix (Bug 16): All datetime.utcnow() calls replaced with
datetime.now(timezone.utc) — utcnow() is deprecated in Python 3.12+.

Key fix (Bug 10 follow-through): Write operations (upsert/insert/update)
now use get_supabase_admin_client() so they bypass RLS on protected tables.
Read operations keep using the anon client.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from backend.db.supabase_client import get_supabase_client, get_supabase_admin_client
from backend.core.logging import get_logger

log = get_logger(__name__)


def _utcnow() -> datetime:
    """Timezone-aware UTC now. Replaces the deprecated datetime.utcnow()."""
    return datetime.now(timezone.utc)


class DatabaseService:
    """
    Central database service for AegisCare.
    All Supabase table operations go through here.

    - self.read_client  → anon key, used for SELECT queries
    - self.write_client → service-role key, used for INSERT/UPDATE/UPSERT/DELETE
    """

    def __init__(self):
        self.read_client = get_supabase_client()
        self.write_client = get_supabase_admin_client()
        self.is_connected = self.read_client is not None

        if self.write_client is None:
            log.warning(
                "DatabaseService: admin (service-role) client unavailable. "
                "All database writes will be skipped. "
                "Set SUPABASE_SERVICE_ROLE_KEY in your .env to enable writes."
            )
        if self.is_connected:
            log.info("DatabaseService initialised with Supabase connection")
        else:
            log.warning("DatabaseService running WITHOUT Supabase (no credentials)")

    # ------------------------------------------------------------------ #
    # Patient records                                                       #
    # ------------------------------------------------------------------ #

    async def save_patient(self, patient_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Insert or upsert a patient record."""
        if not self.write_client:
            return None
        try:
            result = self.write_client.table("patients").upsert(patient_data).execute()
            log.info(f"Patient saved: {patient_data.get('patient_id', '?')}")
            return result.data[0] if result.data else None
        except Exception as e:
            log.error(f"Failed to save patient: {e}")
            return None

    async def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single patient by ID."""
        if not self.read_client:
            return None
        try:
            result = (
                self.read_client.table("patients")
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
        if not self.read_client:
            return []
        try:
            result = self.read_client.table("patients").select("*").execute()
            return result.data or []
        except Exception as e:
            log.error(f"Failed to list patients: {e}")
            return []

    # ------------------------------------------------------------------ #
    # Triage sessions                                                       #
    # ------------------------------------------------------------------ #

    async def save_triage_session(self, session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Insert a new triage session row."""
        if not self.write_client:
            return None
        try:
            result = self.write_client.table("triage_sessions").insert(session_data).execute()
            log.info(f"Triage session saved: {session_data.get('session_id', '?')}")
            return result.data[0] if result.data else None
        except Exception as e:
            log.error(f"Failed to save triage session: {e}")
            return None

    async def get_triage_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a triage session by ID."""
        if not self.read_client:
            return None
        try:
            result = (
                self.read_client.table("triage_sessions")
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
        Falls back to a local dict if Supabase is unavailable.
        """
        session_data = {
            "session_id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "symptoms": symptoms,
            "created_at": _utcnow().isoformat(),
        }

        if not self.write_client:
            log.warning("Supabase not connected — returning local session dict")
            return session_data

        saved = await self.save_triage_session(session_data)
        return saved if saved else session_data

    async def add_symptom(self, session_id: str, symptom: str) -> bool:
        """Record an individual symptom linked to a triage session."""
        if not self.write_client:
            return False
        try:
            data = {
                "session_id": session_id,
                "symptom": symptom,
                "recorded_at": _utcnow().isoformat(),
            }
            self.write_client.table("session_symptoms").insert(data).execute()
            return True
        except Exception as e:
            log.error(f"Failed to add symptom to session {session_id}: {e}")
            return False

    async def update_patient_state(
        self, session_id: str, severity: str, risk_score: int
    ) -> bool:
        """Update severity and risk score on an existing triage session row."""
        if not self.write_client:
            return False
        try:
            self.write_client.table("triage_sessions").update(
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
        if not self.write_client:
            return False
        try:
            data = {
                "session_id": session_id,
                "patient_id": patient_id,
                "generated_at": _utcnow().isoformat(),
                "report_markdown": report_content,
            }
            self.write_client.table("reports").insert(data).execute()
            log.info(f"Handoff report saved for session {session_id}")
            return True
        except Exception as e:
            log.error(f"Failed to save handoff report: {e}")
            return False


db_service = DatabaseService()
