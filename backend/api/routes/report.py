from fastapi import APIRouter, HTTPException
from backend.reports.handoff_report import generate_handoff_report
from backend.db.database_service import db_service
from backend.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/report", tags=["Reports"])


@router.post("/handoff/{session_id}")
async def generate_and_save_report(session_id: str, patient_id: str):
    try:
        # For now, we use placeholder patient state.
        # Later we can fetch real data from database.
        patient_state = {
            "patient_id": patient_id,
            "session_id": session_id,
            "severity": "high",
            "risk_score": 78,
            "symptoms": ["fever", "cough", "breathing difficulty"],
            "conversation_summary": "Patient showing signs of respiratory infection."
        }

        report_content = generate_handoff_report(patient_state)

        # Save to database
        await db_service.save_handoff_report(session_id, patient_id, report_content)

        return {
            "status": "success",
            "message": "Handoff report generated and saved",
            "report": report_content
        }

    except Exception as e:
        log.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")
