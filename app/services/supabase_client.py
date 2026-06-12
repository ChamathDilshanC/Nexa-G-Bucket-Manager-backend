"""Supabase integration helper service.

Author: Chamath Dilshan
"""

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings


@lru_cache
def get_supabase_admin_client() -> Client:
    """Create and return a Supabase client with service-role privileges."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


@lru_cache
def get_supabase_auth_client() -> Client:
    """Create and return a Supabase client for OAuth and session exchange."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)
