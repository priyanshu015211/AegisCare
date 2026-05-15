from fastapi import APIRouter, HTTPException, status, Depends
from backend.schemas.patient import PatientAnalyzeRequest
from backend.ai.memory.patient_memory import PatientMemory
from backend.ai.reasoning.ai_engine import AIEngine
from backend.ai.reasoning.drift_engine import DriftEngine
from backend.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/analyze")
async def analyze_patient(
    request: PatientAnalyzeRequest,
    ai_engine: AIEngine = Depends(get_ai_engine)
):
    try:
        memory = PatientMemory(request.patient_id)
        for symptom in request.symptoms:
            memory.add_symptom(symptom)

        result = await ai_engine.analyze_patient(memory.get_state())

        return {
            "status": "success",
            "patient_id": request.patient_id,
            "analysis": result,
            "current_state": memory.get_state()
        }

    except Exception as e:
        log.error(f"AI analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI analysis failed. Please try again."
        )
