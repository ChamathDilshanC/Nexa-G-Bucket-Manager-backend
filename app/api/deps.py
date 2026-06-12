"""Reusable FastAPI dependencies.

Author: Chamath Dilshan
"""

from fastapi import Header, HTTPException, status

from app.core.security import build_user_context, decode_supabase_jwt
from app.services.bucket_registry import BucketRegistry
from app.services.supabase_storage import SupabaseStorageService


def get_current_user(authorization: str = Header(default="")) -> dict:
    """Extract and validate the bearer token from Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be in format: Bearer <token>.",
        )
    token = authorization.replace("Bearer ", "", 1).strip()
    return decode_supabase_jwt(token)


def get_user_context(authorization: str = Header(default="")) -> dict:
    """Return normalized user context from the validated JWT."""
    return build_user_context(get_current_user(authorization))


def get_storage_service() -> SupabaseStorageService:
    """Create a Supabase storage service instance per request lifecycle."""
    try:
        return SupabaseStorageService()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


def get_bucket_registry() -> BucketRegistry:
    """Create a bucket registry instance per request lifecycle."""
    return BucketRegistry()
