"""
backend/core/auth.py

Authentication dependency for AegisCare API routes.

Bug 17 fix: get_current_user is now a proper FastAPI dependency wired to
every protected route via the router-level dependency in api_v1.py.
Previously this function existed but was never used, leaving all endpoints
fully unauthenticated.

Current implementation accepts a Bearer token in the Authorization header
and performs a basic presence check. The TODO below describes the Supabase
JWT validation that should replace it before going to production.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.core.logging import get_logger

log = get_logger(__name__)

# Tells FastAPI to look for "Authorization: Bearer <token>" on every request
# that declares get_current_user as a dependency.
_bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict:
    """
    FastAPI dependency — validates the Bearer token on protected routes.

    Usage (single route):
        @router.post("/analyze")
        async def analyze(request: ..., user=Depends(get_current_user)):
            ...

    Usage (entire router — preferred, applied in api_v1.py):
        router.include_router(ai_router, dependencies=[Depends(get_current_user)])

    Current behaviour:
        Rejects requests with no token (401) or an empty token (401).
        Returns a minimal user dict so route handlers can access user context.

    TODO: Replace the placeholder check below with real Supabase JWT validation:
        from supabase import create_client
        user = supabase.auth.get_user(credentials.credentials)
        if not user or user.user is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return {"user_id": user.user.id, "role": user.user.role}
    """
    token = credentials.credentials

    if not token:
        log.warning("Request rejected: empty Bearer token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- placeholder: accept any non-empty token in dev ---
    # Replace this block with Supabase JWT validation for production.
    log.debug(f"Authenticated request with token prefix: {token[:8]}...")
    return {"user_id": "authenticated_user", "role": "patient"}
