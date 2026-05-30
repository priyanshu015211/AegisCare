"""
backend/api/routes/ai.py

AI analysis route.  Uses session_id (from PatientAnalyzeRequest) to
key PatientMemory so concurrent triage sessions for the same patient
never overwrite each other's in-memory state.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from backend.schemas.patient import PatientAnalyzeRequest
from backend.ai.memory.patient_memory import PatientMemory
from backend.core.logging import get_logger
from backend.api.dependencies.services import get_ai_engine

log = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/analyze")
async def analyze_patient_ai(
    request: PatientAnalyzeRequest,
    ai_engine=Depends(get_ai_engine)
):
    """
    AI-powered patient analysis using Gemini.
    Returns severity, risk score, reasoning, and follow-up question.

    Each call is scoped to (patient_id, session_id) so parallel triage
    sessions for the same patient remain fully isolated.
    """
    try:
        # Key memory on the composite (patient_id, session_id) so
        # concurrent sessions for the same patient never collide.
        memory_key = f"{request.patient_id}:{request.session_id}"
        memory = PatientMemory(memory_key)

        for symptom in request.symptoms:
            memory.add_symptom(symptom)

        patient_state = memory.get_state()
        patient_state["duration"] = request.duration

        result = await ai_engine.analyze_patient(patient_state)

        memory.update_risk(
            risk_score=result.get("risk_score", 50),
            severity=result.get("severity", "medium"),
            confidence=0.85
        )

        return {
            "status": "success",
            "patient_id": request.patient_id,
            "session_id": request.session_id,   # echo back so callers can track
            "analysis": {
                "severity": result.get("severity"),
                "risk_score": result.get("risk_score"),
                "reasoning": result.get("reasoning"),
                "follow_up_question": result.get("follow_up_question"),
                "escalation_needed": result.get("escalation_needed", False)
            },
            "current_state": memory.get_state()
        }

    except Exception as e:
        log.error(f"AI analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI analysis failed. Please try again."
        )
