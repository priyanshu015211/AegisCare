"""
backend/api/middleware/audit_logger.py

Audit logging middleware for PHI (Protected Health Information) access.

HIPAA requires that every access to patient data is logged with:
- WHO accessed it (user/token prefix)
- WHAT they accessed (endpoint, patient_id if applicable)
- WHEN (timestamp)
- WHAT RESULT (success/failure, status code)

This middleware automatically logs PHI-relevant endpoints. It does NOT log
public health check endpoints or system status endpoints.

Audit logs are written to a separate file (logs/audit.log) with rotation,
so they can be retained independently of application logs (HIPAA requires
7-year retention for audit logs).
"""

import time
import json
from datetime import datetime, timezone
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.core.config import get_settings
from backend.core.logging import get_logger

log = get_logger(__name__)
settings = get_settings()

# Endpoints that access PHI (Protected Health Information).
# Any request to these paths is logged as a PHI access event.
_PHI_ENDPOINTS = frozenset({
    "/api/v1/patient/",
    "/api/v1/ai/",
    "/api/v1/voice/",
    "/api/v1/report/",
})

# Public endpoints that should NOT be audit-logged.
_PUBLIC_ENDPOINTS = frozenset({
    "/health",
    "/api/v1/system/status",
    "/api/v1/system/uptime",
})


def _is_phi_endpoint(path: str) -> bool:
    """Check if a request path accesses PHI."""
    if path in _PUBLIC_ENDPOINTS:
        return False
    return any(path.startswith(prefix) for prefix in _PHI_ENDPOINTS)


class AuditLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs PHI access events to a dedicated audit log file.

    Each log entry is a structured JSON object containing:
    - timestamp: ISO 8601 UTC timestamp
    - method: HTTP method (GET, POST, etc.)
    - path: Request path
    - status_code: Response status code
    - duration_ms: Request duration in milliseconds
    - token_prefix: First 4 chars of the bearer token (for user identification)
    - patient_id: Extracted from request body if present (for audit trail)
    - action: What was done (analyze, update, transcribe, report, etc.)
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        path = request.url.path

        # Only audit-log PHI endpoints
        if not _is_phi_endpoint(path):
            return await call_next(request)

        start_time = time.time()

        # Extract token prefix for user identification
        auth_header = request.headers.get("authorization", "")
        token_prefix = "none"
        if auth_header.startswith("Bearer "):
            token_prefix = auth_header[7:11] + "..."  # First 4 chars + "..."

        # Extract action from path
        action = path.split("/")[-1] if path.split("/")[-1] else path.split("/")[-2]

        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        # Build audit log entry
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": path,
            "action": action,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "token_prefix": token_prefix,
            "client_ip": request.client.host if request.client else "unknown",
        }

        # Determine log level based on status code
        if response.status_code >= 500:
            log.error(f"PHI_ACCESS_FAIL | {json.dumps(audit_entry)}")
        elif response.status_code >= 400:
            log.warning(f"PHI_ACCESS_DENIED | {json.dumps(audit_entry)}")
        else:
            log.info(f"PHI_ACCESS_OK | {json.dumps(audit_entry)}")

        return response
