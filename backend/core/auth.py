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

if not _EXPECTED_TOKEN:
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
