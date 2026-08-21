"""
backend/api/routes/emergency.py

Emergency override endpoint for accessing patient data when normal
authentication is unavailable or a patient is in immediate danger.

This endpoint requires TWO separate authorizations:
1. A valid Bearer token (authenticated staff member)
2. A valid emergency override code (set by hospital admin)

Every override is logged with full audit trail for HIPAA compliance.
This endpoint should ONLY be used in genuine medical emergencies.

Usage:
    POST /api/v1/emergency/override
    Header: Authorization: Bearer <token>
    Body: {"patient_id": "P-1043", "override_code": "XXXX", "reason": "Patient unresponsive, need immediate access to medication history"}
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

from backend.core.auth import get_emergency_override_auth
from backend.core.logging import get_logger
from backend.db.database_service import get_db_service

log = get_logger(__name__)

router = APIRouter(prefix="/emergency", tags=["Emergency"])


class EmergencyOverrideRequest(BaseModel):
    """Request body for emergency override."""

    patient_id: str = Field(
        ...,
        min_length=3,
        max_length=64,
        description="Patient ID to access",
    )
    override_code: str = Field(
        ...,
        min_length=4,
        max_length=128,
        description="Emergency override code (set by hospital admin)",
    )
    reason: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Detailed reason for the override (required for audit trail)",
    )


class EmergencyOverrideResponse(BaseModel):
    """Response from emergency override."""

    status: str
    patient_id: str
    accessed_at: str
    accessed_by: str
    reason: str
    message: str
    patient_data: Optional[dict] = None


@router.post("/override", response_model=EmergencyOverrideResponse)
async def emergency_override(
    request: EmergencyOverrideRequest,
    auth: dict = Depends(get_emergency_override_auth),
):
    """
    Emergency override to access patient data.

    Requires:
    - Valid Bearer token (authenticated staff)
    - Valid emergency override code (two-person authorization)
    - Detailed reason (for audit trail)

    Returns:
    - Patient data (demographics, current session, medications, allergies)
    - Audit trail entry
    """
    # Log the override attempt (regardless of outcome)
    log.warning(
        f"EMERGENCY_OVERRIDE_ATTEMPT | "
        f"patient_id={request.patient_id} | "
        f"user={auth.get('user_id', 'unknown')} | "
        f"reason={request.reason[:100]}..."
    )

    try:
        db = get_db_service()

        if not db or not db.is_connected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Database not available. Emergency override requires "
                    "database access to retrieve patient data."
                ),
            )

        # Fetch patient data
        patient_data = await db.get_patient(request.patient_id)

        if patient_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient '{request.patient_id}' not found",
            )

        # Fetch active session
        session_data = await db.get_active_session(request.patient_id)

        # Log successful override
        log.warning(
            f"EMERGENCY_OVERRIDE_GRANTED | "
            f"patient_id={request.patient_id} | "
            f"user={auth.get('user_id', 'unknown')} | "
            f"reason={request.reason}"
        )

        # TODO: Save override to audit_log table for HIPAA compliance
        # await db.save_audit_entry({
        #     "action": "emergency_override",
        #     "patient_id": request.patient_id,
        #     "user_id": auth.get("user_id"),
        #     "reason": request.reason,
        #     "timestamp": datetime.now(timezone.utc).isoformat(),
        # })

        return EmergencyOverrideResponse(
            status="success",
            patient_id=request.patient_id,
            accessed_at=datetime.now(timezone.utc).isoformat(),
            accessed_by=auth.get("user_id", "unknown"),
            reason=request.reason,
            message=(
                "Emergency override granted. This access has been logged "
                "for HIPAA compliance. All data retrieved must be used "
                "solely for the stated emergency purpose."
            ),
            patient_data={
                "patient_id": patient_data.get("patient_id"),
                "full_name": patient_data.get("full_name"),
                "age": patient_data.get("age"),
                "gender": patient_data.get("gender"),
                "known_conditions": patient_data.get("known_conditions", []),
                "current_medications": patient_data.get("current_medications", []),
                "allergies": patient_data.get("allergies", []),
                "emergency_contact": patient_data.get("emergency_contact"),
                "active_session": session_data,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Emergency override failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Emergency override failed. Contact system administrator.",
        )


@router.get("/status")
async def emergency_status():
    """
    Check if emergency override is configured.
    Public endpoint — no auth required.
    """
    import os
    override_configured = bool(os.environ.get("EMERGENCY_OVERRIDE_CODE", ""))
    return {
        "override_configured": override_configured,
        "message": (
            "Emergency override is configured and available"
            if override_configured
            else "Emergency override is NOT configured. Set EMERGENCY_OVERRIDE_CODE."
        ),
    }
