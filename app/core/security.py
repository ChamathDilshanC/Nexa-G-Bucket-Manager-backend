"""Authentication and token validation logic.

Author: Chamath Dilshan
"""

from datetime import datetime, timezone

import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError

from app.core.config import get_settings


def decode_supabase_jwt(token: str) -> dict:
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
