"""
frontend/utils/api_client.py

Centralized API client for communicating with AegisCare Backend.
Supports both sync and async calls.
"""

import httpx
import os
from typing import Dict, Any, Optional

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class APIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    # ------------------ Async Methods ------------------
    async def post_async(self, endpoint: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{self.base_url}{endpoint}", json=json)
            response.raise_for_status()
            return response.json()

    async def get_async(self, endpoint: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()

    # ------------------ Sync Methods (for Streamlit) ------------------
    def post(self, endpoint: str, json: Optional[Dict] = None) -> Dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(f"{self.base_url}{endpoint}", json=json)
            response.raise_for_status()
            return response.json()

    def get(self, endpoint: str) -> Dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()


# Global instance
api_client = APIClient()
