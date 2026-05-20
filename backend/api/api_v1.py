"""
backend/api/api_v1.py

API v1 router aggregator.
"""

from fastapi import APIRouter

from .routes.system import router as system_router
from .routes.patient import router as patient_router
from .routes.ai import router as ai_router
from .routes.voice import router as voice_router
from .routes.report import router as report_router

# Create the aggregator router FIRST, then include sub-routers
api_router = APIRouter()

api_router.include_router(system_router, prefix="/system", tags=["System"])
api_router.include_router(patient_router)  # already has prefix="/patient"
api_router.include_router(ai_router)       # already has prefix="/ai"
api_router.include_router(voice_router)    # already has prefix="/voice"
api_router.include_router(report_router)   # already has prefix="/report"
