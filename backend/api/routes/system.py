"""
backend/api/routes/system.py

System status and diagnostic endpoints under /api/v1/system

FIX Bug 7: The /uptime endpoint previously lived as a raw @app.get() route
directly in main.py, bypassing the router hierarchy entirely. All
/api/v1/system/* endpoints belong here so they share the same router,
tags, prefix, and middleware chain consistently.

APP_START_TIME is imported from backend.main — that module initialises it
first, so there is no circular import risk (main.py imports api_v1 which
imports this file, but this file only imports APP_START_TIME which is a
plain float set at module load time before any router is wired up).
"""

import time
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


@router.get(
    "/uptime",
    tags=["System"],
    include_in_schema=settings.debug,
    summary="Application Uptime (debug only)"
)
async def get_uptime():
    """
    Returns how long the backend process has been running.
    Only shown in API docs when DEBUG=true.

    Moved here from main.py (Bug 7 fix) — this endpoint now lives in the
    system router alongside /status, mounted at /api/v1/system/uptime via
    api_v1.py. No more hardcoded paths on the app instance.
    """
    # Import here to avoid a circular import at module level.
    # main.py → api_v1.py → system.py is the import chain;
    # importing APP_START_TIME inside the function body breaks the cycle safely.
    from backend.main import APP_START_TIME

    uptime_seconds = time.time() - APP_START_TIME
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    return {
        "uptime_seconds": round(uptime_seconds, 2),
        "uptime_human": f"{hours}h {minutes}m {seconds}s",
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(APP_START_TIME)),
    }
