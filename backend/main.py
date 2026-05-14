"""
backend/main.py

AegisCare FastAPI application entry point.
This file is the Phase 1 structural placeholder.
Full implementation happens in Phase 2.

Run with:
    uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_settings
from backend.core.logging import setup_logging, get_logger

# Initialize logging before anything else
setup_logging()
log = get_logger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AegisCare: AI Emergency Escalation and Healthcare Coordination System. "
        "Built for overloaded hospitals, rural clinics, and emergency triage."
    ),
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS — restrict to known frontend origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    log.info(f"AegisCare backend starting | version={settings.app_version} | env={settings.app_env}")


@app.on_event("shutdown")
async def shutdown_event():
    log.info("AegisCare backend shutting down")


@app.get("/", tags=["Health"])
async def root():
    return {
        "system": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "environment": settings.app_env,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Used by load balancers and Docker healthchecks.
    """
    return {"status": "healthy"}
