"""
backend/api/api_v1.py

API v1 router aggregator.
"""

from fastapi import APIRouter

from .routes.system import router as system_router
from .routes.patient import router as patient_router
from .routes.ai import router as ai_router
from .routes.voice import router as voice_router

api_router = APIRouter()

api_router.include_router(system_router, prefix="/system", tags=["System"])
api_router.include_router(patient_router, prefix="/patient", tags=["Patient"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
api_router.include_router(voice_router, prefix="/voice", tags=["Voice"])
