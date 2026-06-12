"""System info and connectivity schemas.

Author: Chamath Dilshan
"""

from pydantic import BaseModel


class AppInfo(BaseModel):
    """Runtime application metadata."""

    name: str
    env: str
    port: int


class SupabaseInfo(BaseModel):
    """Supabase project connectivity and configuration status."""

    configured: bool
    connected: bool
    url: str | None = None
    project_ref: str | None = None
    jwt_secret_configured: bool
    service_role_key_configured: bool
    error: str | None = None


class BucketInfo(BaseModel):
    """Storage bucket metadata exposed in status responses."""

    name: str
    public: bool | None = None
    file_size_limit: int | None = None
    allowed_mime_types: list[str] | None = None
    created_at: str | None = None
    updated_at: str | None = None


class StorageInfo(BaseModel):
    """Supabase Storage connectivity and bucket summary."""

    connected: bool
    default_bucket: str | None = None
    default_bucket_configured: bool
    default_bucket_exists: bool
    default_bucket_details: BucketInfo | None = None
    total_buckets: int
    buckets: list[BucketInfo]
    error: str | None = None


class SettingsInfo(BaseModel):
    """Non-sensitive runtime settings useful for diagnostics."""

    signed_url_expiry_seconds: int
    max_upload_size_mb: int
    allowed_mime_types: list[str]


class SystemInfoResponse(BaseModel):
    """Full system status payload for monitoring and debugging."""

    status: str
    app: AppInfo
    supabase: SupabaseInfo
    storage: StorageInfo
    settings: SettingsInfo


class ApiLink(BaseModel):
    """Describes a single API route with absolute and relative URLs."""

    name: str
    method: str
    path: str
    url: str
    description: str
    auth_required: bool = False


class DocsLinks(BaseModel):
    """Interactive and machine-readable API documentation links."""

    swagger: ApiLink
    redoc: ApiLink
    openapi: ApiLink


class ConnectivitySummary(BaseModel):
    """Condensed live connectivity snapshot for the root endpoint."""

    overall_status: str
    supabase_connected: bool
    supabase_url: str | None = None
    supabase_project_ref: str | None = None
    storage_connected: bool
    default_bucket: str | None = None
    default_bucket_exists: bool
    total_buckets: int


class RootResponse(BaseModel):
    """Rich API landing page payload with links and connectivity summary."""

    name: str
    description: str
    version: str
    status: str
    environment: str
    base_url: str
    docs: DocsLinks
    connectivity: ConnectivitySummary
    settings: SettingsInfo
    links: list[ApiLink]
    detailed_status_url: str
