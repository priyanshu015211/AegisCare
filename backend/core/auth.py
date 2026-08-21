"""
backend/core/auth.py

Authentication dependency for AegisCare API routes.

Bug 6 fix: the previous implementation accepted any non-empty string as a
valid Bearer token, providing zero actual security. Anyone who sent
"Authorization: Bearer abc" had full access to every protected endpoint.

This version validates the token against the AEGISCARE_TOKEN environment
variable using hmac.compare_digest (constant-time comparison) to prevent
timing attacks. In development, if AEGISCARE_TOKEN is not set, the fallback
value "dev-token" is accepted with a loud warning at startup so existing
local workflows aren't broken.

TODO: Replace the shared-secret check below with real Supabase JWT validation
once the login flow is implemented:
    from supabase import create_client
    user = supabase.auth.get_user(credentials.credentials)
    if not user or user.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"user_id": user.user.id, "role": user.user.role}
"""

import hmac
import os
import warnings

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.core.logging import get_logger

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Shared-secret token (placeholder until Supabase JWT auth is wired up)
# ---------------------------------------------------------------------------

_EXPECTED_TOKEN: str = os.environ.get("AEGISCARE_TOKEN", "")
_is_production = os.environ.get("APP_ENV", "development").lower() == "production"

if not _EXPECTED_TOKEN:
    if _is_production:
        raise RuntimeError(
            "AEGISCARE_TOKEN is not set. This is a REQUIRED environment variable. "
            "Generate a secure token with: python -c \"import secrets; print(secrets.token_hex(32))\" "
            "Then set AEGISCARE_TOKEN to that value in your environment."
        )
    _EXPECTED_TOKEN = "dev-token"
    warnings.warn(
        "WARNING: AEGISCARE_TOKEN is not set. Falling back to the insecure "
        "default 'dev-token'. Set AEGISCARE_TOKEN in your .env file for local "
        "dev and in the Render dashboard for production.",
        stacklevel=2,
    )

# Tells FastAPI to look for "Authorization: Bearer <token>" on every request
# that declares get_current_user as a dependency.
_bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict:
    """
    FastAPI dependency — validates the Bearer token on protected routes.

    Usage (entire router — preferred, applied in api_v1.py):
        api_router.include_router(ai_router, dependencies=[Depends(get_current_user)])

    Current behaviour:
        - Rejects requests with no token (401).
        - Compares the supplied token against AEGISCARE_TOKEN using
          constant-time hmac.compare_digest to prevent timing attacks.
        - Returns a minimal user dict so route handlers can access user context.
    """
    token = credentials.credentials

    if not token:
        log.warning("Request rejected: empty Bearer token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Constant-time comparison prevents timing-based token enumeration.
    token_valid = hmac.compare_digest(
        token.encode("utf-8"),
        _EXPECTED_TOKEN.encode("utf-8"),
    )

    if not token_valid:
        log.warning(f"Request rejected: invalid token (prefix={token[:4]}...)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    log.debug(f"Authenticated request | token_prefix={token[:4]}...")
    return {"user_id": "authenticated_user", "role": "patient"}


# ---------------------------------------------------------------------------
# Emergency override dependency (two-person authorization)
# ---------------------------------------------------------------------------

async def get_emergency_override_auth(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    override_code: str = None,
) -> dict:
    """
    Emergency override endpoint authentication.
    Requires: valid token AND a valid override code.
    The override code is a separate secret that must be set by a hospital admin.
    """
    # First, validate the normal token
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for emergency override",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_valid = hmac.compare_digest(
        token.encode("utf-8"),
        _EXPECTED_TOKEN.encode("utf-8"),
    )
    if not token_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Second, validate the override code
    expected_override = os.environ.get("EMERGENCY_OVERRIDE_CODE", "")
    if not expected_override:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Emergency override is not configured. Set EMERGENCY_OVERRIDE_CODE.",
        )

    if not override_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Emergency override code required",
        )

    override_valid = hmac.compare_digest(
        override_code.encode("utf-8"),
        expected_override.encode("utf-8"),
    )
    if not override_valid:
        log.warning(f"EMERGENCY OVERRIDE DENIED: invalid override code (prefix={override_code[:4]}...)")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid emergency override code",
        )

    log.warning(f"EMERGENCY OVERRIDE GRANTED | user_prefix={token[:4]}...")
    return {"user_id": "authenticated_user", "role": "emergency_override", "override": True}
