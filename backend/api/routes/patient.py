"""
backend/api/routes/patient.py
"""

"""
backend/api/routes/patient.py

Bug 6 fix: RiskScoringService and DriftDetectionService were wired as
injectable singletons in services.py but never injected or called by any
route. PatientService used its own _calculate_placeholder_risk() instead.

The services are now injected here and their results are used:
  - RiskScoringService.calculate_risk() replaces _calculate_placeholder_risk()
    for the /analyze endpoint, giving a richer risk breakdown.
  - DriftDetectionService.detect_drift() is called with the current
    symptoms list on /update so symptom-progression drift is surfaced.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from backend.schemas.patient import PatientAnalyzeRequest, PatientUpdateRequest
from backend.schemas.responses import PatientAnalysisResponse, PatientUpdateResponse
from backend.api.dependencies.services import PatientServiceDep, RiskServiceDep, DriftServiceDep
from backend.core.logging import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/patient", tags=["Patient"])


@router.post("/analyze", response_model=PatientAnalysisResponse)
async def analyze_patient(
    request: PatientAnalyzeRequest,
    patient_service: PatientServiceDep,
    risk_service: RiskServiceDep,          # Bug 6: now actually used
):
    try:
        # Use RiskScoringService instead of the internal placeholder
        risk_result = await risk_service.calculate_risk(
            symptoms=request.symptoms,
            duration=request.duration,
        )

        result = await patient_service.analyze_symptoms(
            patient_id=request.patient_id,
            symptoms=request.symptoms,
            duration=request.duration,
            # Pass the computed risk so patient_service doesn't re-calculate
            risk_score=risk_result["risk_score"],
            severity=risk_result["severity"],
        )

        return PatientAnalysisResponse(
            patient_id=result["patient_id"],
            session_id=result.get("session_id"),
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
    patient_service: PatientServiceDep,
    drift_service: DriftServiceDep,        # Bug 6: now actually used
):
    try:
        result = await patient_service.update_patient_state(
            patient_id=request.patient_id,
            new_symptom=request.new_symptom,
        )

        # Run drift detection on the accumulated symptom history
        drift_result = await drift_service.detect_drift(
            symptoms_history=result.get("all_symptoms", [request.new_symptom])
        )
        if drift_result["drift_detected"]:
            log.warning(
                f"Drift detected for patient {request.patient_id}: "
                f"escalation_risk={drift_result['escalation_risk']}"
            )

        return PatientUpdateResponse(
            patient_id=result["patient_id"],
            new_symptom=result["new_symptom"],
            updated_risk_score=result["updated_risk_score"],
            severity=result["severity"],
            message=result["message"],
        )
    except Exception as e:
        log.error(f"Error updating patient: {e}")
        raise HTTPException(status_code=500, detail="Failed to update patient")
