"""System connectivity and configuration status checks.

Author: Chamath Dilshan
"""

from typing import Any
from urllib.parse import urlparse

from app.core.config import Settings, get_settings
from app.services.supabase_client import get_supabase_admin_client
from app.services.supabase_storage import SupabaseStorageService


def _extract_project_ref(url: str) -> str | None:
    """Extract the Supabase project ref from the project URL."""
    hostname = urlparse(url).hostname or ""
    if hostname.endswith(".supabase.co"):
        return hostname.removesuffix(".supabase.co")
    return None


def _bucket_from_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Return bucket fields used by the info response schema."""
    return {
        "name": data["name"],
        "public": data.get("public"),
        "file_size_limit": data.get("file_size_limit"),
        "allowed_mime_types": data.get("allowed_mime_types"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
    }


def _check_supabase(settings: Settings) -> dict[str, Any]:
    """Validate Supabase configuration and live connectivity."""
    configured = bool(settings.supabase_url and settings.supabase_service_role_key)
    info: dict[str, Any] = {
        "configured": configured,
        "connected": False,
        "url": settings.supabase_url or None,
        "project_ref": _extract_project_ref(settings.supabase_url) if settings.supabase_url else None,
        "jwt_secret_configured": bool(settings.supabase_jwt_secret),
        "service_role_key_configured": bool(settings.supabase_service_role_key),
        "error": None,
    }

    if not configured:
        info["error"] = "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured."
        return info

    try:
        client = get_supabase_admin_client()
        client.storage.list_buckets()
        info["connected"] = True
    except Exception as exc:  # pragma: no cover - provider-specific failures
        info["error"] = str(exc)

    return info


def _check_storage(settings: Settings, supabase_connected: bool) -> dict[str, Any]:
    """Validate storage connectivity and default bucket availability."""
    default_bucket = settings.supabase_default_bucket or None
    info: dict[str, Any] = {
        "connected": False,
        "default_bucket": default_bucket,
        "default_bucket_configured": bool(default_bucket),
        "default_bucket_exists": False,
        "default_bucket_details": None,
        "total_buckets": 0,
        "buckets": [],
        "error": None,
    }

    if not supabase_connected:
        info["error"] = "Storage is unavailable because Supabase is not connected."
        return info

    try:
        storage = SupabaseStorageService()
        buckets = storage.list_buckets()
        info["connected"] = True
        info["total_buckets"] = len(buckets)
        info["buckets"] = [_bucket_from_dict(bucket) for bucket in buckets]

        if default_bucket:
            matching = next((bucket for bucket in buckets if bucket["name"] == default_bucket), None)
            if matching:
                info["default_bucket_exists"] = True
                info["default_bucket_details"] = _bucket_from_dict(matching)
            else:
                info["error"] = f"Default bucket '{default_bucket}' was not found in Supabase Storage."
    except Exception as exc:  # pragma: no cover - provider-specific failures
        info["error"] = str(exc)

    return info


def _check_database(supabase_connected: bool) -> dict[str, Any]:
    """Verify the user bucket ownership table is available."""
    info: dict[str, Any] = {
        "user_buckets_table_ready": False,
        "error": None,
    }

    if not supabase_connected:
        info["error"] = "Database checks are unavailable because Supabase is not connected."
        return info

    try:
        client = get_supabase_admin_client()
        client.table("user_buckets").select("id").limit(1).execute()
        info["user_buckets_table_ready"] = True
    except Exception as exc:  # pragma: no cover - provider-specific failures
        info["error"] = str(exc)

    return info


def _resolve_status(
    supabase: dict[str, Any],
    storage: dict[str, Any],
    database: dict[str, Any],
) -> str:
    """Derive an overall health status from component checks."""
    if supabase["connected"] and storage["connected"] and database["user_buckets_table_ready"]:
        if storage["default_bucket_configured"] and not storage["default_bucket_exists"]:
            return "degraded"
        return "ok"
    if supabase["configured"] or storage["default_bucket_configured"]:
        return "degraded"
    return "error"


def get_system_info() -> dict[str, Any]:
    """Build the full JSON status payload for the info endpoint."""
    settings = get_settings()
    supabase = _check_supabase(settings)
    storage = _check_storage(settings, supabase_connected=supabase["connected"])
    database = _check_database(supabase_connected=supabase["connected"])

    return {
        "status": _resolve_status(supabase, storage, database),
        "app": {
            "name": settings.app_name,
            "env": settings.app_env,
            "port": settings.app_port,
        },
        "supabase": supabase,
        "storage": storage,
        "database": database,
        "settings": {
            "signed_url_expiry_seconds": settings.signed_url_expiry_seconds,
            "max_upload_size_mb": settings.max_upload_size_mb,
            "allowed_mime_types": sorted(settings.parsed_allowed_mime_types),
        },
    }
