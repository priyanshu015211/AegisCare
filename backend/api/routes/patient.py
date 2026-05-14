"""
backend/api/routes/patient.py
"""

from fastapi import APIRouter, HTTPException, status, Depends
from backend.schemas.patient import PatientAnalyzeRequest, PatientUpdateRequest
from backend.schemas.responses import PatientAnalysisResponse, PatientUpdateResponse
from backend.api.dependencies.services import PatientServiceDep
from backend.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/patient", tags=["Patient"])


@router.post("/analyze", response_model=PatientAnalysisResponse)
async def analyze_patient(
    request: PatientAnalyzeRequest,
    patient_service: PatientServiceDep
):
    try:
        result = await patient_service.analyze_symptoms(
            patient_id=request.patient_id,
            symptoms=request.symptoms,
            duration=request.duration,
        )
        return PatientAnalysisResponse(
            patient_id=result["patient_id"],
            severity=result["severity"],
            risk_score=result["risk_score"],
            confidence=0.82,
            message=result["message"],
        )
    except Exception as e:
        log.error(f"Error in patient analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze patient")


@router.post("/update", response_model=PatientUpdateResponse)
async def update_patient(
    request: PatientUpdateRequest,
    patient_service: PatientServiceDep
):
    try:
        result = await patient_service.update_patient_state(
            patient_id=request.patient_id,
            new_symptom=request.new_symptom,
        )
        return PatientUpdateResponse(
            patient_id=result["patient_id"],
            updated_risk_score=result["updated_risk_score"],
            severity=result["severity"],
            message=result["message"],
        )
    except Exception as e:
        log.error(f"Error updating patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to update patient")
