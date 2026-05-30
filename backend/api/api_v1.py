"""
backend/api/api_v1.py

API v1 router aggregator.

Bug 17 fix: get_current_user is now applied as a router-level dependency
on all protected routers (patient, ai, voice, report). This means every
endpoint in those routers requires a valid Bearer token automatically —
no need to add Depends(get_current_user) to each route individually.

The system router is intentionally left public (health checks, status).
"""

from fastapi import APIRouter, Depends

from .routes.system import router as system_router
from .routes.patient import router as patient_router
from .routes.ai import router as ai_router
from .routes.voice import router as voice_router
from .routes.report import router as report_router
from backend.core.auth import get_current_user

# Auth dependency applied to all protected routers at once
_auth = [Depends(get_current_user)]

api_router = APIRouter()

# Public — no auth required (health checks, readiness probes)
api_router.include_router(system_router, prefix="/system", tags=["System"])

# Protected — every endpoint requires a valid Bearer token
api_router.include_router(patient_router, dependencies=_auth)
api_router.include_router(ai_router, dependencies=_auth)
api_router.include_router(voice_router, dependencies=_auth)
api_router.include_router(report_router, dependencies=_auth)
