"""
backend/db/database_service.py

DatabaseService — thin async wrapper around the Supabase admin client.

Provides all database operations used by the AegisCare services:
  - create_session()         → INSERT a new triage session
  - add_symptom()            → INSERT a symptom record for a session
  - update_patient_state()   → UPDATE session severity + risk score
  - get_triage_session()     → SELECT a session + its symptoms
  - save_handoff_report()    → INSERT a generated handoff report

Design decisions:
  - All methods are async and return dicts (or None on failure) so callers
    never need to import Supabase types directly.
  - Every public method catches its own exceptions, logs them, and returns
    a safe falsy value.  The service layer must check the return value and
    handle None gracefully — it must never assume a write succeeded.
  - Uses get_supabase_admin_client() (service-role key) for all writes so
    Row Level Security does not silently block inserts.
  - is_connected is a cheap cached property; it does not perform a live
    network check — it only tests whether the client was initialised.
"""

from typing import Any, Dict, List, Optional
from backend.db.supabase_client import get_supabase_admin_client, get_supabase_client
from backend.core.logging import get_logger

log = get_logger(__name__)


class DatabaseService:
    """
    Async database access layer for AegisCare.

    Usage (via dependency injection):
        from backend.db.database_service import get_db_service
        db = get_db_service()
        if db.is_connected:
            session = await db.create_session(patient_id, symptoms)
    """

    # ------------------------------------------------------------------
    # Connectivity
    # ------------------------------------------------------------------

    @property
    def is_connected(self) -> bool:
        """
        True when at least the anon Supabase client is available.
        Does NOT perform a live network round-trip.
        """
        return get_supabase_client() is not None

    # ------------------------------------------------------------------
    # Sessions
    # ------------------------------------------------------------------

    async def create_session(
        self,
        patient_id: str,
        symptoms: List[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Insert a new triage session row and return it.

        Returns the inserted row dict (including server-generated session_id)
        or None if the insert failed.
        """
        client = get_supabase_admin_client()
        if client is None:
            log.warning("create_session: Supabase admin client not available")
            return None

        try:
            result = (
                client.table("sessions")
                .insert(
                    {
                        "patient_id": patient_id,
                        "symptoms": symptoms,
                        "severity": "low",
                        "risk_score": 0,
                        "status": "active",
                    }
                )
                .execute()
            )

            if result.data:
                row = result.data[0]
                log.info(
                    f"Session created | session_id={row.get('session_id')} "
                    f"patient_id={patient_id}"
                )
                return row

            log.warning(
                f"create_session returned no data for patient_id={patient_id}"
            )
            return None

        except Exception as exc:
            log.error(f"create_session failed for patient_id={patient_id}: {exc}")
            return None

    # ------------------------------------------------------------------
    # Symptoms
    # ------------------------------------------------------------------

    async def add_symptom(
        self,
        session_id: str,
        symptom: str,
    ) -> bool:
        """
        Insert a single symptom record linked to a session.

        Returns True on success, False on failure.
        """
        client = get_supabase_admin_client()
        if client is None:
            log.warning("add_symptom: Supabase admin client not available")
            return False

        try:
            result = (
                client.table("symptom_records")
                .insert({"session_id": session_id, "symptom": symptom})
                .execute()
            )
            return bool(result.data)

        except Exception as exc:
            log.error(
                f"add_symptom failed | session_id={session_id} symptom={symptom!r}: {exc}"
            )
            return False

    # ------------------------------------------------------------------
    # Patient / Session State
    # ------------------------------------------------------------------

    async def update_patient_state(
        self,
        session_id: str,
        severity: str,
        risk_score: int,
    ) -> bool:
        """
        Update the severity and risk_score on an existing session row.

        Returns True on success, False on failure.
        """
        client = get_supabase_admin_client()
        if client is None:
            log.warning("update_patient_state: Supabase admin client not available")
            return False

        try:
            result = (
                client.table("sessions")
                .update({"severity": severity, "risk_score": risk_score})
                .eq("session_id", session_id)
                .execute()
            )
            if result.data:
                log.info(
                    f"Session state updated | session_id={session_id} "
                    f"severity={severity} risk_score={risk_score}"
                )
                return True

            log.warning(
                f"update_patient_state matched no rows for session_id={session_id}"
            )
            return False

        except Exception as exc:
            log.error(
                f"update_patient_state failed | session_id={session_id}: {exc}"
            )
            return False

    # ------------------------------------------------------------------
    # Session Fetch
    # ------------------------------------------------------------------

    async def get_triage_session(
        self,
        session_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a session row and its associated symptom records.

        Returns a dict with keys:
          session_id, patient_id, severity, risk_score, symptoms (list),
          conversation_summary, escalation_history, confidence, status
        or None if the session does not exist.
        """
        client = get_supabase_client()
        if client is None:
            log.warning("get_triage_session: Supabase client not available")
            return None

        try:
            # Fetch the session row
            session_result = (
                client.table("sessions")
                .select("*")
                .eq("session_id", session_id)
                .execute()
            )

            if not session_result.data:
                log.info(f"get_triage_session: no session found for id={session_id}")
                return None

            session = session_result.data[0]

            # Fetch all symptoms linked to this session
            symptoms_result = (
                client.table("symptom_records")
                .select("symptom")
                .eq("session_id", session_id)
                .execute()
            )

            symptom_list: List[str] = []
            if symptoms_result.data:
                symptom_list = [row["symptom"] for row in symptoms_result.data]

            # Merge into a single response dict
            return {
                "session_id": str(session.get("session_id", session_id)),
                "patient_id": session.get("patient_id", ""),
                "severity": session.get("severity", "unknown"),
                "risk_score": session.get("risk_score", 0),
                "symptoms": symptom_list or session.get("symptoms", []),
                "conversation_summary": session.get(
                    "summary", "No summary recorded for this session."
                ),
                "escalation_history": [],   # populated in a future phase
                "confidence": 0.0,
                "status": session.get("status", "unknown"),
            }

        except Exception as exc:
            log.error(f"get_triage_session failed for session_id={session_id}: {exc}")
            return None

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    async def save_handoff_report(
        self,
        session_id: str,
        patient_id: str,
        report_content: str,
    ) -> bool:
        """
        Insert a generated handoff report into the reports table.

        Returns True on success, False on failure.
        Always safe to call — will not raise even if the DB is unavailable.
        """
        client = get_supabase_admin_client()
        if client is None:
            log.warning(
                "save_handoff_report: Supabase admin client not available — "
                "report was generated but not persisted."
            )
            return False

        try:
            result = (
                client.table("reports")
                .insert(
                    {
                        "session_id": session_id,
                        "patient_id": patient_id,
                        "report_markdown": report_content,
                    }
                )
                .execute()
            )

            if result.data:
                log.info(
                    f"Handoff report saved | session_id={session_id} "
                    f"patient_id={patient_id}"
                )
                return True

            log.warning(
                f"save_handoff_report returned no data for session_id={session_id}"
            )
            return False

        except Exception as exc:
            log.error(
                f"save_handoff_report failed | session_id={session_id}: {exc}"
            )
            return False


# ------------------------------------------------------------------
# Singleton factory  (mirrors the pattern in supabase_client.py)
# ------------------------------------------------------------------

_db_service: Optional["DatabaseService"] = None


def get_db_service() -> "DatabaseService":
    """
    Returns a shared DatabaseService instance, creating it on first call.
    Thread-safe enough for a single-process uvicorn deployment.
    FastAPI Depends() works cleanly with this pattern.
    """
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
        log.info("DatabaseService singleton created")
    return _db_service
