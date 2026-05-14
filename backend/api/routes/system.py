"""
backend/api/routes/system.py

System status and diagnostic endpoints under /api/v1/system
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from backend.core.config import get_settings

router = APIRouter(tags=["System"])

settings = get_settings()


@router.get("/status", summary="System Status")
async def system_status():
    return {
        "status": "operational",
        "version": settings.app_version,
        "environment": settings.app_env,
        "debug_mode": settings.debug,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "api": "healthy",
            "config": "loaded",
            "logging": "active"
        }
    }
