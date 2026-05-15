"""
backend/api/routes/ai.py

AI Reasoning and Memory endpoints.
"""

from fastapi import APIRouter
from backend.schemas.patient import PatientAnalyzeRequest
from backend.ai.memory.patient_memory import PatientMemory
from backend.ai.reasoning.ai_engine import AIEngine
from backend.ai.reasoning.drift_engine import DriftEngine
from backend.api.dependencies.services import get_ai_engine, get_drift_engine   # Using DI

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/analyze")
async def analyze_patient(
    request: PatientAnalyzeRequest,
    ai_engine: AIEngine = Depends(get_ai_engine),           # Injected
    drift_engine: DriftEngine = Depends(get_drift_engine)   # Injected (optional here)
):
    """Main AI analysis endpoint."""
    memory = PatientMemory(request.patient_id)
    for symptom in request.symptoms:
        memory.add_symptom(symptom)

    # Fixed: Changed from analyze_symptoms() → analyze_patient()
    result = await ai_engine.analyze_patient(memory.get_state())

    return {
        "status": "success",
        "patient_id": request.patient_id,
        "analysis": result,
        "current_state": memory.get_state()
    }


@router.post("/drift/analyze")
async def analyze_drift(
    patient_id: str,
    previous_symptoms: list[str],
    new_symptoms: list[str],
    drift_engine: DriftEngine = Depends(get_drift_engine)
):
    result = drift_engine.detect_drift(previous_symptoms, new_symptoms)
    return {"status": "success", "patient_id": patient_id, "drift_analysis": result}
