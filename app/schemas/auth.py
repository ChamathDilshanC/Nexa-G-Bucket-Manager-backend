"""Authentication API schemas.

Author: Chamath Dilshan
"""

from pydantic import BaseModel, Field


class GoogleAuthResponse(BaseModel):
    """OAuth initiation payload."""

    provider: str
    url: str


class AuthCallbackRequest(BaseModel):
    """Payload used to exchange an OAuth callback code for a session."""

    code: str = Field(min_length=8)


class AuthUserResponse(BaseModel):
    """Authenticated user profile derived from JWT claims."""

    user_id: str
    email: str | None = None
    role: str | None = None
    provider: str | None = None
    is_google_user: bool = False


class AuthRefreshRequest(BaseModel):
    """Payload used to refresh an expired access token."""

    refresh_token: str = Field(min_length=8)


class AuthSessionResponse(BaseModel):
    """Session tokens returned after Google OAuth callback."""

    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = None
    token_type: str = "bearer"
    user: dict[str, str | None]
