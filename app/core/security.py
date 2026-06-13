"""Authentication and token validation logic.

Author: Chamath Dilshan
"""

from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError, PyJWKClient

from app.core.config import get_settings


@lru_cache
def get_jwks_client(supabase_url: str) -> PyJWKClient:
    """Create a cached JWKS client for Supabase asymmetric JWT verification."""
    jwks_url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url, cache_keys=True)


def decode_supabase_jwt(token: str) -> dict[str, Any]:
    """Validate a Supabase JWT and return its decoded claims."""
    settings = get_settings()

    try:
        header = jwt.get_unverified_header(token)
        algorithm = header.get("alg", "HS256")

        if algorithm == "HS256":
            if not settings.supabase_jwt_secret:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="SUPABASE_JWT_SECRET is not configured on the server.",
                )
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        elif algorithm in {"ES256", "RS256"}:
            if not settings.supabase_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="SUPABASE_URL is not configured on the server.",
                )
            signing_key = get_jwks_client(settings.supabase_url).get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=[algorithm],
                options={"verify_aud": False},
                leeway=10,
            )
        else:
            raise InvalidTokenError(f"Unsupported JWT algorithm: {algorithm}")
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
