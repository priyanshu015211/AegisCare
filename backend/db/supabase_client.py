"""
backend/db/supabase_client.py

Supabase client for AegisCare.
- anon_key client  → read-only / public queries (respects RLS)
- service_role client → writes / upserts / inserts (bypasses RLS)

Always use get_supabase_admin_client() for any database write operation,
because Supabase enables RLS by default and the anon key will produce
silent 403 failures on protected tables.
"""

from supabase import create_client, Client
from backend.core.config import get_settings
from backend.core.logging import get_logger
from typing import Optional

log = get_logger(__name__)
settings = get_settings()

# Singletons — created once, reused forever
_anon_client: Optional[Client] = None
_admin_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Returns an anon-key Supabase client.
    Use this for SELECT queries on public / RLS-open tables only.
    For any INSERT / UPDATE / UPSERT / DELETE use get_supabase_admin_client().
    """
    global _anon_client

    if _anon_client is not None:
        return _anon_client

    if not settings.supabase_url or not settings.supabase_anon_key:
        log.warning("Supabase anon credentials not configured. Running without database.")
        return None

    try:
        _anon_client = create_client(settings.supabase_url, settings.supabase_anon_key)
        log.info("Supabase anon client initialised successfully")
        return _anon_client
    except Exception as e:
        log.error(f"Failed to initialise Supabase anon client: {e}")
        return None


def get_supabase_admin_client() -> Optional[Client]:
    """
    Returns a service-role Supabase client that bypasses Row Level Security.

    Required for all write operations (INSERT, UPDATE, UPSERT, DELETE)
    on tables that have RLS enabled (the Supabase default).  Using the
    anon key for writes causes silent 403 errors that are swallowed by
    except blocks, resulting in data that appears to be saved but isn't.

    Keep this client server-side only — never expose the service_role key
    to the browser or return it in any API response.
    """
    global _admin_client

    if _admin_client is not None:
        return _admin_client

    if not settings.supabase_url or not settings.supabase_service_role_key:
        log.warning(
            "Supabase service_role_key not configured. "
            "Database writes will fail on RLS-protected tables. "
            "Set SUPABASE_SERVICE_ROLE_KEY in your .env file."
        )
        return None

    try:
        _admin_client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )
        log.info("Supabase admin (service-role) client initialised successfully")
        return _admin_client
    except Exception as e:
        log.error(f"Failed to initialise Supabase admin client: {e}")
        return None


def is_supabase_connected() -> bool:
    """True if at least the anon client is available."""
    return get_supabase_client() is not None
