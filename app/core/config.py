"""Application settings and environment management.

Author: Chamath Dilshan
"""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Nexa-G-Bucket Manager API"
    app_env: str = "development"
    app_port: int = 8000
    app_cors_origins: str = "*"

    supabase_url: str = ""
    supabase_jwt_secret: str = ""

    gcp_project_id: str = ""
    gcp_default_bucket: str | None = None
    gcp_service_account_json: str = ""

    signed_url_expiry_seconds: int = 900
    max_upload_size_mb: int = 50
    allowed_mime_types: str = "image/jpeg,image/png,application/pdf"

    @field_validator("signed_url_expiry_seconds")
    @classmethod
    def validate_expiry(cls, value: int) -> int:
        """Keep signed URL expiry in a secure and practical range."""
        if value < 60 or value > 3600:
            msg = "SIGNED_URL_EXPIRY_SECONDS must be between 60 and 3600."
            raise ValueError(msg)
        return value

    @property
    def parsed_cors_origins(self) -> list[str]:
        """Convert comma-separated CORS origins into a clean list."""
        if self.app_cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.app_cors_origins.split(",") if origin.strip()]

    @property
    def parsed_allowed_mime_types(self) -> set[str]:
        """Convert allowed mime types string into a set for quick checks."""
        return {
            mime.strip()
            for mime in self.allowed_mime_types.split(",")
            if mime.strip()
        }


@lru_cache
def get_settings() -> Settings:
    """Load and cache settings to avoid repeated environment parsing."""
    return Settings()
