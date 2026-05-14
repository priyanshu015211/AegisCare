import httpx
import os
from typing import Dict, Any

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class APIClient:
    def __init__(self):
        self.base_url = BACKEND_URL

    async def post(self, endpoint: str, json: Dict[str, Any] = None):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}{endpoint}", json=json, timeout=30)
            response.raise_for_status()
            return response.json()

    async def get(self, endpoint: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}{endpoint}", timeout=30)
            response.raise_for_status()
            return response.json()

api_client = APIClient()
