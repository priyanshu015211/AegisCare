"""
backend/db/supabase_client.py

Improved Supabase client for AegisCare.
Handles connection, error logging, and provides a clean interface.
"""

from supabase import create_client, Client
from backend.core.config import get_settings
from backend.core.logging import get_logger
from typing import Optional, Dict, Any, List

log = get_logger(__name__)
settings = get_settings()

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Returns a Supabase client instance.
    Creates the client only once (singleton pattern).
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    if not settings.supabase_url or not settings.supabase_anon_key:
        log.warning("Supabase credentials not found in .env. Running without database.")
        return None

    try:
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
        log.info("Supabase client initialized successfully")
        return _supabase_client

    except Exception as e:
        log.error(f"Failed to initialize Supabase client: {e}")
        return None


# ============================================================
# Helper Functions (We will expand these)
# ============================================================

def is_supabase_connected() -> bool:
    """Check if Supabase client is available."""
    return get_supabase_client() is not None
