"""
backend/db/database_service.py

Central Database Service for AegisCare.
Handles all interactions with Supabase in a clean and organized way.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.db.supabase_client import get_supabase_client
from backend.core.logging import get_logger

log = get_logger(__name__)


class DatabaseService:
    def __init__(self):
        self.client = get_supabase_client()
        self.is_connected = self.client is not None

        if not self.is_connected:
            log.warning("DatabaseService initialized without Supabase connection.")

    # ============================================================
    # Session Management
    # ============================================================

    async def create_session(self, patient_id: str, initial_symptoms: List[str] = None) -> Optional[Dict]:
        """Create a new patient session."""
        if not self.is_connected:
            return None

        try:
            data = {
                "patient_id": patient_id,
                "started_at": datetime.utcnow().isoformat(),
                "symptoms": initial_symptoms or [],
                "severity": "low",
                "risk_score": 0,
                "status": "active"
            }

            response = self.client.table("sessions").insert(data).execute()
            log.info(f"Session created for patient {patient_id}")
            return response.data[0] if response.data else None

        except Exception as e:
            log.error(f"Failed to create session: {e}")
            return None

    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        if not self.is_connected:
            return None

        try:
            response = self.client.table("sessions").select("*").eq("session_id", session_id).single().execute()
            return response.data
        except Exception as e:
            log.error(f"Failed to get session: {e}")
            return None

    # ============================================================
    # Symptom Tracking
    # ============================================================

    async def add_symptom(self, session_id: str, symptom: str) -> bool:
        """Add a new symptom to a session."""
        if not self.is_connected:
            return False

        try:
            # This assumes you have a 'symptom_records' table
            data = {
                "session_id": session_id,
                "symptom": symptom.lower(),
                "reported_at": datetime.utcnow().isoformat()
            }

            self.client.table("symptom_records").insert(data).execute()
            log.info(f"Symptom '{symptom}' added to session {session_id}")
            return True

        except Exception as e:
            log.error(f"Failed to add symptom: {e}")
            return False

    # ============================================================
    # Patient State Update
    # ============================================================

    async def update_patient_state(
        self, 
        session_id: str, 
        severity: str, 
        risk_score: int
    ) -> bool:
        """Update severity and risk score of a session."""
        if not self.is_connected:
            return False

        try:
            self.client.table("sessions").update({
                "severity": severity,
                "risk_score": risk_score,
                "last_updated": datetime.utcnow().isoformat()
            }).eq("session_id", session_id).execute()

            log.info(f"Session {session_id} updated → Severity: {severity}, Risk: {risk_score}")
            return True

        except Exception as e:
            log.error(f"Failed to update patient state: {e}")
            return False

    # ============================================================
    # Reports
    # ============================================================

    async def save_handoff_report(self, session_id: str, patient_id: str, report_content: str) -> bool:
        """Save doctor handoff report."""
        if not self.is_connected:
            return False

        try:
            data = {
                "session_id": session_id,
                "patient_id": patient_id,
                "generated_at": datetime.utcnow().isoformat(),
                "report_markdown": report_content
            }

            self.client.table("reports").insert(data).execute()
            log.info(f"Handoff report saved for session {session_id}")
            return True

        except Exception as e:
            log.error(f"Failed to save handoff report: {e}")
            return False


# Global instance
db_service = DatabaseService()
