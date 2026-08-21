"""
backend/api/dependencies/services.py

Dependency Injection providers for AegisCare services.
Use these with FastAPI's `Depends()` for clean service injection.

FIX Bug 5: Replaced @lru_cache() on service factory functions with an explicit
module-level singleton pattern.

The problem with @lru_cache() here:
- lru_cache caches the return value forever across the process lifetime with
  no way to invalidate it. If a service holds a broken connection (e.g. Supabase
  dropped), the broken instance is served to every subsequent request.
- lru_cache is not thread/async-safe for initialisation — two concurrent
  requests hitting a cold cache could race to create two instances.
- It obscures intent: FastAPI's Depends() already handles per-request vs
  shared lifetime; mixing lru_cache on top creates confusion.

The fix uses plain module-level variables initialised to None and a small
_get_or_create() helper. Services are still singletons (created once, reused),
but the pattern is explicit, easy to test, and safe to reset in tests by
setting the module variable back to None.
"""

from typing import Annotated, Optional
from fastapi import Depends

from backend.services.patient_service import PatientService
from backend.services.risk_service import RiskScoringService
from backend.services.drift_service import DriftDetectionService
from backend.ai.reasoning.ai_engine import AIEngine
from backend.ai.reasoning.drift_engine import DriftEngine
from backend.db.database_service import DatabaseService, get_db_service

# ============================================================
# Module-level singleton holders — None until first request
# ============================================================

_patient_service: Optional[PatientService] = None
_risk_service: Optional[RiskScoringService] = None
_ai_engine: Optional[AIEngine] = None
_drift_engine: Optional[DriftEngine] = None
_drift_service: Optional[DriftDetectionService] = None


# ============================================================
# Service factory functions
# ============================================================

def get_patient_service() -> PatientService:
    """
    Returns a shared PatientService instance, creating it on first call.
    Safe to use with FastAPI Depends() — no lru_cache needed.
    """
    global _patient_service
    if _patient_service is None:
        _patient_service = PatientService()
    return _patient_service


def get_risk_service() -> RiskScoringService:
    """Returns a shared RiskScoringService instance."""
    global _risk_service
    if _risk_service is None:
        _risk_service = RiskScoringService()
    return _risk_service


def get_ai_engine() -> AIEngine:
    """
    Returns a shared AIEngine instance.
    The Gemini client inside AIEngine is initialised here on first call,
    not at import time, so a missing API key does not crash startup.
    """
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIEngine()
    return _ai_engine


def get_drift_engine() -> DriftEngine:
    """Returns a shared DriftEngine instance."""
    global _drift_engine
    if _drift_engine is None:
        _drift_engine = DriftEngine()
    return _drift_engine


def get_drift_service() -> DriftDetectionService:
    """Returns a shared DriftDetectionService instance."""
    global _drift_service
    if _drift_service is None:
        _drift_service = DriftDetectionService()
    return _drift_service


# ============================================================
# Type aliases for clean usage in route files
# ============================================================

PatientServiceDep = Annotated[PatientService, Depends(get_patient_service)]
RiskServiceDep = Annotated[RiskScoringService, Depends(get_risk_service)]
AI_EngineDep = Annotated[AIEngine, Depends(get_ai_engine)]
Drift_EngineDep = Annotated[DriftEngine, Depends(get_drift_engine)]
DriftServiceDep = Annotated[DriftDetectionService, Depends(get_drift_service)]
DBServiceDep = Annotated[DatabaseService, Depends(get_db_service)]
