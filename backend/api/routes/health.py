"""
backend/api/routes/health.py

Health and root endpoints for AegisCare API.
These are public endpoints for monitoring and basic info.
"""

from fastapi import APIRouter
from backend.core.config import get_settings

router = APIRouter(tags=["Health"])

settings = get_settings()


@router.get("/", summary="API Root")
async def root():
    return {
        "system": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "environment": settings.app_env,
        "message": "AegisCare backend is running. See /docs for API documentation."
    }


@router.get("/health", summary="Health Check")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }
