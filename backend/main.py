"""
backend/main.py

AegisCare FastAPI application entry point.
Phase 2A: Backend Foundation Setup — Complete modular foundation.

This module initializes the FastAPI application with:
- Structured logging (Loguru)
- CORS middleware (configurable via .env)
- Error handling middleware + consistent exception handlers
- Modular API routing under /api/v1
- Modern lifespan context manager (replaces deprecated on_event)
- Health, root, and system status endpoints
- Uptime endpoint (debug mode)

Run with:
    uvicorn backend.main:app --reload --port 8000
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_settings
from backend.core.logging import setup_logging, get_logger

# Modular route imports
from backend.api.routes.health import router as health_router
from backend.api.api_v1 import api_router

# Error handling
from backend.api.middleware.error_handler import ErrorHandlerMiddleware, add_exception_handlers

# Initialize logging very early
setup_logging()
log = get_logger(__name__)

settings = get_settings()

# Simple in-memory start time for uptime reporting
APP_START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern lifespan handler.
    Preferred over @app.on_event in FastAPI >= 0.93+.
    Place heavy initialization (DB pools, model loading) here in later phases.
    """
    log.info(
        f"AegisCare backend starting | "
        f"version={settings.app_version} | "
        f"env={settings.app_env} | "
        f"debug={settings.debug}"
    )
    yield
    log.info("AegisCare backend shutting down gracefully")


# ============================================================
# APPLICATION INSTANCE
# ============================================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AegisCare — AI Emergency Escalation & Healthcare Coordination System\n\n"
        "Production-grade backend for overloaded hospitals, rural clinics, "
        "and emergency triage. Built with FastAPI, structured logging, "
        "modular routing, and consistent error handling."
    ),
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# ============================================================
# MIDDLEWARE STACK
# ============================================================

# CORS (origins from .env ALLOWED_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized error handling (catches crashes and returns consistent JSON)
app.add_middleware(ErrorHandlerMiddleware)

# Explicit exception handlers for HTTPException and generic errors
add_exception_handlers(app)


# ============================================================
# ROUTER INCLUSION
# ============================================================

# Health & root endpoints (mounted at top level for monitoring tools & simplicity)
app.include_router(health_router)

# All versioned business routes live under /api/v1
app.include_router(api_router, prefix="/api/v1")


# ============================================================
# ADDITIONAL DEBUG / OPERATIONS ENDPOINTS
# ============================================================

@app.get(
    "/api/v1/system/uptime",
    tags=["System"],
    include_in_schema=settings.debug,
    summary="Application Uptime (debug only)"
)
async def get_uptime():
    """Returns how long the backend has been running. Useful for debugging and health dashboards."""
    uptime_seconds = time.time() - APP_START_TIME
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    return {
        "uptime_seconds": round(uptime_seconds, 2),
        "uptime_human": f"{hours}h {minutes}m {seconds}s",
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(APP_START_TIME)),
    }


# ============================================================
# ENTRYPOINT (for direct python execution)
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        workers=settings.backend_workers,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
