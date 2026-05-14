"""
backend/api/api_v1.py

API v1 router aggregator.
"""

from fastapi import APIRouter
from .routes.system import router as system_router
from .routes.patient import router as patient_router   # Added in 2B

api_router = APIRouter()

api_router.include_router(system_router, prefix="/system", tags=["System"])
api_router.include_router(patient_router, prefix="/patient", tags=["Patient"])
from .patient import router as patient_router

__all__ = ["health_router", "system_router", "patient_router"]
