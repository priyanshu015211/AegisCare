"""
backend/db/supabase_client.py

Supabase client initialization for AegisCare.
"""

from supabase import create_client, Client
from backend.core.config import get_settings
from backend.core.logging import get_logger

log = get_logger(__name__)
settings = get_settings()


_supabase_client: Client = None


def get_supabase_client() -> Client:
    global _supabase_client

    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_anon_key:
            log.warning("Supabase credentials not found. Running without database.")
            return None

        try:
            _supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            log.info("Supabase client initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize Supabase client: {e}")
            return None

    return _supabase_client
