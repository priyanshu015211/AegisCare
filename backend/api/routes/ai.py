from fastapi import APIRouter
from backend.schemas.patient import PatientAnalyzeRequest
from backend.ai.memory.patient_memory import PatientMemory
from backend.ai.reasoning.ai_engine import AIEngine
from backend.ai.reasoning.drift_engine import DriftEngine

router = APIRouter(prefix="/ai", tags=["AI"])
ai_engine = AIEngine()
drift_engine = DriftEngine()

@router.post("/analyze")
async def analyze_patient(request: PatientAnalyzeRequest):
    memory = PatientMemory(request.patient_id)
    for s in request.symptoms:
        memory.add_symptom(s)
    result = await ai_engine.analyze_symptoms(memory.get_state())
    return {"status": "success", "analysis": result, "state": memory.get_state()}

@router.post("/drift/analyze")
async def analyze_drift(patient_id: str, previous_symptoms: list, new_symptoms: list):
    result = drift_engine.detect_drift(previous_symptoms, new_symptoms)
    return {"status": "success", "drift": result}
