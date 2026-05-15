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
            # We can extend the response model later to include session_id
        )
    except Exception as e:
        log.error(f"Error in patient analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze patient")
