"""
backend/api/middleware/request_logger.py

Middleware for structured request logging using Loguru.
Logs every incoming request with useful metadata.
"""

from typing import Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from backend.core.logging import get_logger

log = get_logger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Logs basic information about every HTTP request.
    Includes method, path, client IP, and response status.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        client_host = request.client.host if request.client else "unknown"

        log.info(
            f"Incoming request | "
            f"{request.method} {request.url.path} | "
            f"client={client_host}"
        )

        response = await call_next(request)

        log.info(
            f"Request completed | "
            f"{request.method} {request.url.path} | "
            f"status={response.status_code}"
        )

        return response
