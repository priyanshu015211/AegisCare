"""
backend/api/routes/patient.py

Patient API routes for AegisCare.
Phase 2B: Foundational patient analysis and update endpoints.

These endpoints demonstrate clean architecture:
- Strong Pydantic validation
- Service layer separation
- Consistent response models
- Async design
"""

from fastapi import APIRouter, HTTPException, status
from backend.schemas.patient import PatientAnalyzeRequest, PatientUpdateRequest
from backend.schemas.responses import PatientAnalysisResponse, PatientUpdateResponse
from backend.services.patient_service import patient_service
from backend.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/patient", tags=["Patient"])


@router.post(
    "/analyze",
    response_model=PatientAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze patient symptoms (initial assessment)",
    description="Accepts initial symptoms and returns placeholder risk assessment."
)
async def analyze_patient(request: PatientAnalyzeRequest):
    """
    Endpoint: POST /api/v1/patient/analyze

    This is currently a placeholder. In later phases it will:
    - Use Dynamic Emergency Drift Detection
    - Call Gemini for reasoning
    - Persist to Supabase
    """
    try:
        result = await patient_service.analyze_patient(
            patient_id=request.patient_id,
            symptoms=request.symptoms,
            duration=request.duration,
            language=request.language,
        )

        return PatientAnalysisResponse(
            patient_id=result["patient_id"],
            severity=result["severity"],
            risk_score=result["risk_score"],
            confidence=result["confidence"],
            message=result["message"],
        )

    except Exception as e:
        log.error(f"Error in patient analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze patient symptoms"
        )


@router.post(
    "/update",
    response_model=PatientUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update patient with new symptom",
    description="Handles symptom progression during an ongoing session."
)
async def update_patient(request: PatientUpdateRequest):
    """
    Endpoint: POST /api/v1/patient/update

    Used when patient reports a new symptom mid-session.
    Triggers updated risk evaluation (placeholder for now).
    """
    try:
        result = await patient_service.update_patient_condition(
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
        log.error(f"Error updating patient condition: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient condition"
        )
