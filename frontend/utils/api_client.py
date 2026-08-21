"""
frontend/utils/api_client.py

Centralised API client for communicating with the AegisCare backend.
Supports both sync (Streamlit) and async call patterns.

Bug 2 fix (was Bug 12 in the report):
    The previous version did `from backend.core.config import get_settings`
    to read BACKEND_URL.  This creates a hard import dependency from the
    Streamlit frontend process into the FastAPI backend package.  On Render
    the two services are deployed independently, and even locally this means
    the frontend process loads all of backend/core/ (Pydantic settings,
    logging setup, etc.) just to read a single URL string.

    The fix reads BACKEND_URL directly from the environment with os.getenv(),
    which is exactly what pydantic-settings was doing under the hood anyway.
    The frontend no longer imports anything from the backend package.

Bug 3 fix:
    All protected backend routes require "Authorization: Bearer <token>".
    The client injects the token on every request.  The token is read from
    the AEGISCARE_TOKEN environment variable (set in .env locally, and in
    the Render dashboard for production).
"""

import os
from typing import Any, Dict, Optional

import httpx


# ---------------------------------------------------------------------------
# Configuration — read directly from environment, no backend import needed
# ---------------------------------------------------------------------------

BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

# Static bearer token for the placeholder auth layer.
# Replace with a real Supabase JWT from a login flow once auth is complete.
_DEFAULT_TOKEN: str = os.getenv("AEGISCARE_TOKEN", "dev-token")


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class APIClient:
    """
    Thin HTTP client that wraps httpx and injects auth headers automatically.

    Construct once per Streamlit session (or use the module-level `api_client`
    singleton for simple cases).  Call set_token() after a successful login
    to switch from the dev token to a real JWT.
    """

    def __init__(
        self,
        base_url: str = BACKEND_URL,
        token: str = _DEFAULT_TOKEN,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Auth helpers
    # ------------------------------------------------------------------

    @property
    def _auth_headers(self) -> Dict[str, str]:
        """Returns the Authorization header dict injected on every request."""
        return {"Authorization": f"Bearer {self._token}"}

    def set_token(self, token: str) -> None:
        """Update the bearer token (e.g. after a Supabase login flow)."""
        self._token = token

    # ------------------------------------------------------------------
    # Async methods
    # ------------------------------------------------------------------

    async def post_async(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                json=json,
                headers=self._auth_headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_async(self, endpoint: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self._auth_headers,
            )
            response.raise_for_status()
            return response.json()

    # ------------------------------------------------------------------
    # Sync methods (Streamlit runs in a synchronous context by default)
    # ------------------------------------------------------------------

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(
                f"{self.base_url}{endpoint}",
                json=json,
                headers=self._auth_headers,
            )
            response.raise_for_status()
            return response.json()

    def get(self, endpoint: str) -> Dict[str, Any]:
        with httpx.Client(timeout=self._timeout) as client:
            response = client.get(
                f"{self.base_url}{endpoint}",
                headers=self._auth_headers,
            )
            response.raise_for_status()
            return response.json()


# ---------------------------------------------------------------------------
# Module-level singleton — use this in Streamlit pages for simple cases
# ---------------------------------------------------------------------------

api_client = APIClient()
