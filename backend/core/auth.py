"""
backend/core/auth.py

Basic authentication utilities (placeholder for future Supabase Auth).
"""

from fastapi import HTTPException, status
from backend.core.logging import get_logger

log = get_logger(__name__)


async def get_current_user(token: str = None):
    """
    Placeholder for user authentication.
    In future, this will validate Supabase JWT tokens.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    # TODO: Validate token with Supabase
    return {"user_id": "demo_user", "role": "patient"}
