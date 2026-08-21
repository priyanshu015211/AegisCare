"""
backend/api/middleware/timing.py

Middleware to measure and log request execution time.
Adds 'X-Process-Time' header to responses.
"""

import time
from typing import Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from backend.core.logging import get_logger

log = get_logger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Measures how long each request takes to process.
    Useful for performance monitoring and observability.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000  # in milliseconds

        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        # Log slow requests
        if process_time > 500:
            log.warning(f"Slow request: {request.method} {request.url.path} took {process_time:.2f}ms")

        return response
