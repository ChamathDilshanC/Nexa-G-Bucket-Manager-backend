"""Authentication and token validation logic.

Author: Chamath Dilshan
"""

from datetime import datetime, timezone
from typing import Any

import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError

from app.core.config import get_settings


def decode_supabase_jwt(token: str) -> dict[str, Any]:
    """Validate a Supabase JWT and return its decoded claims."""
    settings = get_settings()
    if not settings.supabase_jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_JWT_SECRET is not configured on the server.",
        )
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        ) from exc

    expiry = payload.get("exp")
    if expiry and datetime.fromtimestamp(expiry, tz=timezone.utc) < datetime.now(tz=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired.",
        )
    return payload


def get_user_id(payload: dict[str, Any]) -> str:
    """Extract the authenticated Supabase user id from JWT claims."""
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing a user id.",
        )
    return str(user_id)


def build_user_context(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize JWT claims into a stable user context object."""
    user_metadata = payload.get("user_metadata") or {}
    app_metadata = payload.get("app_metadata") or {}
    provider = app_metadata.get("provider") or user_metadata.get("provider")

    return {
        "user_id": get_user_id(payload),
        "email": payload.get("email"),
        "role": payload.get("role"),
        "provider": provider,
        "is_google_user": provider == "google",
    }
