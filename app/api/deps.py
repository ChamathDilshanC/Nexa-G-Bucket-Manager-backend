"""Reusable FastAPI dependencies.

Author: Chamath Dilshan
"""

from fastapi import Header, HTTPException, status

from app.core.security import decode_supabase_jwt
from app.services.gcp_storage import GCPStorageService


def get_current_user(authorization: str = Header(default="")) -> dict:
    """Extract and validate the bearer token from Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be in format: Bearer <token>.",
        )
    token = authorization.replace("Bearer ", "", 1).strip()
    return decode_supabase_jwt(token)


def get_storage_service() -> GCPStorageService:
    """Create a GCP storage service instance per request lifecycle."""
    try:
        return GCPStorageService()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
