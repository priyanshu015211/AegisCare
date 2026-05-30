"""
frontend/utils/api_client.py

Centralized API client for communicating with AegisCare Backend.
Supports both sync and async calls.

Bug 3 fix: all protected backend routes require an "Authorization: Bearer
<token>" header. The previous client sent no auth headers, so every API
call from the frontend returned a 401 and nothing worked.

The client now accepts a token at construction time and injects it as a
Bearer header on every request. The token is read from the AEGISCARE_TOKEN
environment variable by default so it can be set in the deployment env
without hardcoding it here.

Bug 12 fix: the previous code read BACKEND_URL with a raw os.getenv() call,
completely bypassing the Pydantic settings system. This meant that if
BACKEND_URL was set via the .env file it would be picked up, but the value
was never validated, never type-checked, and was inconsistent with the
settings.backend_url field defined in config.py. Anyone who set backend_url
in settings expecting it to flow through to the API client would see no effect.

Now we import get_settings() and read settings.backend_url as the single
source of truth. The .env key (BACKEND_URL) still works unchanged because
pydantic-settings maps it automatically — the only difference is the value
now goes through the same validated, cached settings object as everything
else in the backend.

NOTE: The backend's current auth is a placeholder that accepts any
non-empty token (see auth.py). Once real Supabase JWT auth is wired up,
replace the AEGISCARE_TOKEN env var approach with a proper login flow that
stores the JWT in Streamlit session_state and passes it here.
"""

import httpx
import os
from typing import Dict, Any, Optional

from backend.core.config import get_settings

_settings = get_settings()

# Single source of truth — reads BACKEND_URL env var via pydantic-settings,
# with the same default and validation as everything else in the app.
BACKEND_URL = _settings.backend_url

# Read a static token from the environment for the placeholder auth layer.
# Replace with a real Supabase JWT from a login flow once auth is complete.
_DEFAULT_TOKEN = os.getenv("AEGISCARE_TOKEN", "dev-token")


class APIClient:
    def __init__(self, base_url: str = BACKEND_URL, token: str = _DEFAULT_TOKEN):
        self.base_url = base_url.rstrip("/")
        self._token = token

    @property
    def _auth_headers(self) -> Dict[str, str]:
        """Returns the Authorization header dict for every request."""
        return {"Authorization": f"Bearer {self._token}"}

    def set_token(self, token: str) -> None:
        """Update the bearer token (e.g. after a Supabase login flow)."""
        self._token = token

    # ------------------ Async Methods ------------------
    async def post_async(self, endpoint: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}{endpoint}", json=json, headers=self._auth_headers
            )
            response.raise_for_status()
            return response.json()

    async def get_async(self, endpoint: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}{endpoint}", headers=self._auth_headers
            )
            response.raise_for_status()
            return response.json()

    # ------------------ Sync Methods (for Streamlit) ------------------
    def post(self, endpoint: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.base_url}{endpoint}", json=json, headers=self._auth_headers
            )
            response.raise_for_status()
            return response.json()

    def get(self, endpoint: str) -> Dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{self.base_url}{endpoint}", headers=self._auth_headers
            )
            response.raise_for_status()
            return response.json()


# Global instance — token sourced from AEGISCARE_TOKEN env var
api_client = APIClient()
