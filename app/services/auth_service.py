"""Supabase authentication helpers for Google OAuth and session exchange.

Author: Chamath Dilshan
"""

from typing import Any

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.services.supabase_client import get_supabase_auth_client


class AuthService:
    """Wraps Supabase Auth flows used by the API."""

    def get_google_oauth_url(self, redirect_to: str | None = None) -> dict[str, str]:
        """Return the Google OAuth URL that starts login or sign-up."""
        settings = get_settings()
        if not settings.supabase_url or not settings.supabase_anon_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SUPABASE_URL and SUPABASE_ANON_KEY must be configured for Google auth.",
            )

        client = get_supabase_auth_client()
        response = client.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {
                    "redirect_to": redirect_to or settings.google_oauth_redirect_url,
                },
            }
        )
        return {
            "provider": response.provider,
            "url": response.url,
        }

    def exchange_auth_code(self, auth_code: str, redirect_to: str | None = None) -> dict[str, Any]:
        """Exchange an OAuth callback code for a Supabase session."""
        settings = get_settings()
        client = get_supabase_auth_client()
        response = client.auth.exchange_code_for_session(
            {
                "auth_code": auth_code,
                "redirect_to": redirect_to or settings.google_oauth_redirect_url,
            }
        )

        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create a session from the provided auth code.",
            )

        user = response.user or response.session.user
        return self._session_to_dict(response)

    def refresh_session(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an expired access token using a Supabase refresh token."""
        client = get_supabase_auth_client()
        response = client.auth.refresh_session(refresh_token)

        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to refresh session with the provided refresh token.",
            )

        return self._session_to_dict(response)

    @staticmethod
    def _session_to_dict(response: Any) -> dict[str, Any]:
        """Normalize a Supabase auth response into an API session payload."""
        session = response.session
        user = response.user or (session.user if session else None)
        provider = None
        if user and user.app_metadata:
            provider = user.app_metadata.get("provider")

        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "expires_in": session.expires_in,
            "token_type": "bearer",
            "user": {
                "id": user.id if user else None,
                "email": user.email if user else None,
                "provider": provider or "google",
            },
        }
