"""
backend/main.py

AegisCare FastAPI application entry point.
Phase 2C: Backend Configuration, Middleware & Error Handling System

This module initializes the FastAPI application with:
- Structured logging (Loguru)
- Multiple production-grade middleware (Security, Logging, Timing, CORS, Error Handling)
- Modular API routing under /api/v1
- Modern lifespan context manager
- Health, root, and system status endpoints

Run with:
    uvicorn backend.main:app --reload --port 8000

FIX Bug 7: Removed the hardcoded @app.get("/api/v1/system/uptime") route that
was defined directly on the app instance in this file. That pattern is
architecturally wrong — all /api/v1/system/* routes belong in
backend/api/routes/system.py and are mounted via api_router. Having one system
endpoint here and the rest in system.py created an inconsistency and a latent
path collision risk if system.py ever added its own /uptime endpoint.

APP_START_TIME is still defined here (this module starts first), and system.py
imports it to power the /uptime endpoint cleanly.
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

# Phase 2C Middleware
from backend.api.middleware.request_logger import RequestLoggerMiddleware
from backend.api.middleware.timing import TimingMiddleware
from backend.api.middleware.security_headers import SecurityHeadersMiddleware

# Initialize logging very early
setup_logging()
log = get_logger(__name__)

settings = get_settings()

# Exposed at module level so system.py can import it for the /uptime endpoint.
APP_START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern lifespan handler.
    Preferred over @app.on_event in FastAPI >= 0.93+.
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
        "and emergency triage."
    ),
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# ============================================================
# MIDDLEWARE STACK (Order matters - outermost first)
# ============================================================

# 1. Security Headers (should be one of the first)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Request Logging
app.add_middleware(RequestLoggerMiddleware)

# 3. Request Timing + Performance header
app.add_middleware(TimingMiddleware)

# 4. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Error Handling (should be close to the application)
app.add_middleware(ErrorHandlerMiddleware)

# Explicit exception handlers
add_exception_handlers(app)


# ============================================================
# ROUTER INCLUSION
# ============================================================

app.include_router(health_router)
app.include_router(api_router, prefix="/api/v1")


# ============================================================
# ENTRYPOINT
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
