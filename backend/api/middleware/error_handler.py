"""
backend/api/middleware/error_handler.py

Centralized error handling middleware and exception handlers for AegisCare.

Provides consistent JSON error responses matching the APIError schema
used across the platform. Logs all errors appropriately.
"""

import time
import traceback
from datetime import datetime, timezone
from typing import Callable

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.config import get_settings
from backend.core.logging import get_logger

log = get_logger(__name__)
settings = get_settings()


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware that catches unhandled exceptions and returns
    consistent error responses. Also logs details for debugging.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            if settings.debug:
                log.debug(f"{request.method} {request.url.path} completed in {process_time:.2f}ms")
            return response
        except HTTPException as exc:
            log.warning(
                f"HTTPException: {exc.status_code} | {request.method} {request.url.path} | {exc.detail}"
            )
            raise exc
        except Exception as exc:
            error_id = f"ERR-{int(time.time())}"
            log.error(
                f"Unhandled exception [{error_id}] on {request.method} {request.url.path}: {str(exc)}"
            )
            if settings.debug:
                log.debug(traceback.format_exc())

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "code": "error",
                    "message": "An unexpected error occurred. Please contact support if the issue persists.",
                    "detail": str(exc) if settings.debug else None,
                    "error_id": error_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )


def add_exception_handlers(app):
    """Register custom exception handlers on the FastAPI app."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        log.warning(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": "error",
                "message": exc.detail,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        error_id = f"ERR-{int(time.time())}"
        log.error(f"Unhandled exception [{error_id}] on {request.url.path}: {str(exc)}")
        if settings.debug:
            log.debug(traceback.format_exc())

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": "error",
                "message": "Internal server error",
                "detail": str(exc) if settings.debug else "Contact system administrator",
                "error_id": error_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
