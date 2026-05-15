"""
backend/api/dependencies/services.py

Dependency Injection providers for AegisCare services.
Use these with FastAPI's `Depends()` for clean service injection.
"""

from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from backend.services.patient_service import PatientService
from backend.services.risk_service import RiskScoringService
from backend.services.drift_service import DriftDetectionService
from backend.ai.reasoning.ai_engine import AIEngine
from backend.ai.reasoning.drift_engine import DriftEngine

# ============================================================
# Service Providers (Cached using lru_cache)
# ============================================================

@lru_cache()
def get_patient_service() -> PatientService:
    """Returns a cached instance of PatientService."""
    return PatientService()


@lru_cache()
def get_risk_service() -> RiskScoringService:
    """Returns a cached instance of RiskScoringService."""
    return RiskScoringService()

@lru_cache()
def get_ai_engine() -> AIEngine:
    return AIEngine()

@lru_cache()
def get_drift_engine() -> DriftEngine:
    return DriftEngine()


AI_EngineDep = Annotated[AIEngine, Depends(get_ai_engine)]
Drift_EngineDep = Annotated[DriftEngine, Depends(get_drift_engine)]

# ============================================================
# Type Aliases for Clean Usage in Routes
# ============================================================

PatientServiceDep = Annotated[PatientService, Depends(get_patient_service)]
RiskServiceDep = Annotated[RiskScoringService, Depends(get_risk_service)]
DriftServiceDep = Annotated[DriftDetectionService, Depends(get_drift_service)]
