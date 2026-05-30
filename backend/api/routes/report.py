from fastapi import APIRouter, HTTPException, status
from backend.models.api_schemas import ReportRequest
from backend.reports.handoff_report import generate_handoff_report
# FIX Bug 4: Import the lazy factory instead of the old module-level singleton.
# `db_service` no longer exists; use get_db_service() so the DatabaseService
# is only created on first use, not at import time.
from backend.db.database_service import get_db_service
from backend.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/report", tags=["Reports"])


@router.post("/handoff")
async def generate_handoff_report_endpoint(
    request: ReportRequest
):
    """
    Generate and save a doctor handoff report.
    """
    session_id = request.session_id
    patient_id = request.patient_id
    try:
        # In real usage, we should fetch actual patient data from DB
        patient_state = {
            "patient_id": patient_id,
            "session_id": session_id,
            "severity": "high",
            "risk_score": 78,
            "symptoms": ["fever", "cough", "breathing difficulty"],
            "conversation_summary": "Patient showing progressive respiratory symptoms."
        }

        report_content = generate_handoff_report(patient_state)

        # Save to Supabase via lazy factory — no crash risk at import time
        db = get_db_service()
        saved = await db.save_handoff_report(session_id, patient_id, report_content)

        return {
            "status": "success",
            "message": "Handoff report generated and saved successfully",
            "saved_to_db": saved,
            "report": report_content
        }

    except Exception as e:
        log.error(f"Failed to generate handoff report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate handoff report"
        )
