"""
backend/api/routes/report.py

FIX Bug 9 (original): The /handoff endpoint previously ignored the session_id
and patient_id from the request entirely, and instead built a hardcoded
patient_state dict with fixed values (severity="high", risk_score=78,
symptoms=["fever","cough","breathing difficulty"]). Every generated report
was identical fiction regardless of which patient or session was requested.

Fix: fetch the real triage session from the database using session_id, then
build patient_state from that real data. Falls back gracefully with a 404 if
the session doesn't exist in the DB, and falls back to a minimal patient_state
if the DB is unavailable (no Supabase credentials) so the endpoint still
works in development without a database.

FIX Bug 4 (database_service.py): uses get_db_service() lazy factory instead
of the old module-level db_service singleton (which no longer exists).

FIX Bug 5 (unconditional save): the previous code called
    saved = await db.save_handoff_report(...)
unconditionally at the bottom of the function, even in the branch where
db.is_connected is False. When the DB is unavailable, db is still a valid
DatabaseService instance (is_connected just returns False), but calling
save_handoff_report on it was wasteful and would log confusing warnings.
The save is now guarded by the same is_connected check used above.
"""

from fastapi import APIRouter, HTTPException, status
from backend.models.api_schemas import ReportRequest
from backend.reports.handoff_report import generate_handoff_report
from backend.db.database_service import get_db_service
from backend.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/report", tags=["Reports"])


@router.post("/handoff")
async def generate_handoff_report_endpoint(
    request: ReportRequest,
):
    """
    Generate and save a doctor handoff report for a triage session.

    Fetches the real session data from the database so the report reflects
    the actual patient's symptoms, severity, and risk score.

    Behaviour by DB state:
      - DB connected + session found   → real report, persisted to DB
      - DB connected + session missing → 404
      - DB unavailable                 → placeholder report, not persisted
    """
    session_id = request.session_id
    patient_id = request.patient_id

    try:
        db = get_db_service()

        # ------------------------------------------------------------------ #
        # Fetch real session data (Bug 9 fix)                                  #
        # ------------------------------------------------------------------ #
        session_data = None

        if db.is_connected:
            session_data = await db.get_triage_session(session_id)

            if session_data is None:
                # Session was requested but doesn't exist in the DB
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Triage session '{session_id}' not found. "
                        f"Ensure the session was created via "
                        f"/api/v1/patient/analyze first."
                    ),
                )

        if session_data:
            # Build patient_state from the real DB record
            patient_state = {
                "patient_id": session_data.get("patient_id", patient_id),
                "session_id": session_id,
                "severity": session_data.get("severity", "unknown"),
                "risk_score": session_data.get("risk_score", 0),
                "symptoms": session_data.get("symptoms", []),
                "conversation_summary": session_data.get(
                    "conversation_summary",
                    "No summary recorded for this session.",
                ),
                "escalation_history": session_data.get("escalation_history", []),
                "confidence": session_data.get("confidence", 0.0),
            }
        else:
            # DB unavailable — build a minimal state so development
            # environments can still generate a placeholder report.
            log.warning(
                "Database unavailable — generating report with minimal data. "
                "Connect Supabase to generate reports from real session data."
            )
            patient_state = {
                "patient_id": patient_id,
                "session_id": session_id,
                "severity": "unknown",
                "risk_score": 0,
                "symptoms": [],
                "conversation_summary": (
                    "Report generated without database access. "
                    "Session data could not be retrieved."
                ),
                "escalation_history": [],
                "confidence": 0.0,
            }

        report_content = generate_handoff_report(patient_state)

        # ------------------------------------------------------------------ #
        # Persist report — only when the DB is reachable (Bug 5 fix)          #
        # ------------------------------------------------------------------ #
        saved = False
        if db.is_connected:
            saved = await db.save_handoff_report(session_id, patient_id, report_content)

        return {
            "status": "success",
            "message": "Handoff report generated successfully"
            + (" and saved to database" if saved else " (not persisted — DB unavailable)"),
            "saved_to_db": saved,
            "report": report_content,
        }

    except HTTPException:
        # Re-raise 404s and other intentional HTTP errors without wrapping them
        raise
    except Exception as exc:
        log.error(f"Failed to generate handoff report: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate handoff report",
        )
