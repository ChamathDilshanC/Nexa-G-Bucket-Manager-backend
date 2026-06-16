"""Authentication endpoints for Google OAuth and JWT session discovery.

Author: Chamath Dilshan
"""

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_user_context
from app.schemas.auth import (
    AuthCallbackRequest,
    AuthRefreshRequest,
    AuthSessionResponse,
    AuthUserResponse,
    GoogleAuthResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google", response_model=GoogleAuthResponse)
def start_google_auth(redirect_to: str | None = None) -> GoogleAuthResponse:
    """Start Google login or sign-up and return the Supabase OAuth URL."""
    payload = AuthService().get_google_oauth_url(redirect_to=redirect_to)
    return GoogleAuthResponse(**payload)


@router.get("/callback", response_model=AuthSessionResponse)
def google_auth_callback(code: str = Query(min_length=8)) -> AuthSessionResponse:
    """Handle the Google OAuth browser redirect and return a Supabase session."""
    session = AuthService().exchange_auth_code(auth_code=code)
    return AuthSessionResponse(**session)


@router.post("/callback", response_model=AuthSessionResponse)
def exchange_google_auth_code(payload: AuthCallbackRequest) -> AuthSessionResponse:
    """Exchange a Google OAuth code for Supabase access and refresh tokens."""
    session = AuthService().exchange_auth_code(
        auth_code=payload.code,
        redirect_to=payload.redirect_to,
    )
    return AuthSessionResponse(**session)


@router.post("/refresh", response_model=AuthSessionResponse)
def refresh_auth_session(payload: AuthRefreshRequest) -> AuthSessionResponse:
    """Refresh an expired access token using a valid refresh token."""
    session = AuthService().refresh_session(payload.refresh_token)
    return AuthSessionResponse(**session)


@router.get("/me", response_model=AuthUserResponse)
def get_authenticated_user(user: dict = Depends(get_user_context)) -> AuthUserResponse:
    """Return the authenticated user profile decoded from the JWT."""
    return AuthUserResponse(**user)
