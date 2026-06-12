"""API discovery payload builder for the root endpoint.

Author: Chamath Dilshan
"""

from app.core.config import get_settings
from app.schemas.info import ApiLink, ConnectivitySummary, DocsLinks, RootResponse, SettingsInfo
from app.services.system_status import get_system_info

API_VERSION = "1.0.0"
API_DESCRIPTION = (
    "Backend API for Nexa-G-Bucket Manager. Handles Supabase JWT auth, "
    "Supabase Storage bucket management, and signed upload/download URLs."
)


def _absolute_url(base_url: str, path: str) -> str:
    """Join a base URL with an API path."""
    return f"{base_url.rstrip('/')}{path}"


def _api_link(
    base_url: str,
    *,
    name: str,
    method: str,
    path: str,
    description: str,
    auth_required: bool = False,
) -> ApiLink:
    """Build a standardized API link object."""
    return ApiLink(
        name=name,
        method=method,
        path=path,
        url=_absolute_url(base_url, path),
        description=description,
        auth_required=auth_required,
    )


def build_root_response(base_url: str) -> RootResponse:
    """Build the enriched root endpoint payload."""
    settings = get_settings()
    system_info = get_system_info()
    default_bucket = settings.supabase_default_bucket or "your-bucket"
    files_path = f"/buckets/{default_bucket}/files"
    delete_file_path = f"/buckets/{default_bucket}/files/example.png"

    links = [
        _api_link(
            base_url,
            name="Health Check",
            method="GET",
            path="/health",
            description="Simple liveness probe for uptime monitoring.",
        ),
        _api_link(
            base_url,
            name="System Info",
            method="GET",
            path="/info",
            description="Full Supabase, storage, and configuration diagnostics.",
        ),
        _api_link(
            base_url,
            name="Google Login",
            method="GET",
            path="/auth/google",
            description="Start Google login or sign-up and receive the Supabase OAuth URL.",
        ),
        _api_link(
            base_url,
            name="Auth Callback",
            method="GET",
            path="/auth/callback?code=your_auth_code",
            description="Exchange a Google OAuth callback code for JWT access and refresh tokens.",
        ),
        _api_link(
            base_url,
            name="Current User",
            method="GET",
            path="/auth/me",
            description="Return the authenticated user profile from the JWT.",
            auth_required=True,
        ),
        _api_link(
            base_url,
            name="List Buckets",
            method="GET",
            path="/buckets",
            description="List buckets owned by the authenticated user.",
            auth_required=True,
        ),
        _api_link(
            base_url,
            name="Create Bucket",
            method="POST",
            path="/buckets",
            description="Create another user-owned Supabase Storage bucket.",
            auth_required=True,
        ),
        _api_link(
            base_url,
            name="Update Bucket",
            method="PATCH",
            path=f"/buckets/{default_bucket}",
            description="Update bucket visibility, MIME types, or file size limit.",
            auth_required=True,
        ),
        _api_link(
            base_url,
            name="Delete Bucket",
            method="DELETE",
            path=f"/buckets/{default_bucket}",
            description="Delete a bucket. Use force=true to empty it first.",
            auth_required=True,
        ),
        _api_link(
            base_url,
            name="List Files",
            method="GET",
            path=files_path,
            description="List files inside a bucket. Optional prefix query supported.",
            auth_required=True,
        ),
        _api_link(
            base_url,
            name="Delete File",
            method="DELETE",
            path=delete_file_path,
            description="Delete a single file from a bucket by object path.",
            auth_required=True,
        ),
        _api_link(
            base_url,
            name="Upload Signed URL",
            method="POST",
            path="/files/upload-url",
            description="Generate a signed upload URL and token for direct client uploads.",
            auth_required=True,
        ),
        _api_link(
            base_url,
            name="Download Signed URL",
            method="POST",
            path="/files/download-url",
            description="Generate a signed download URL for a stored object.",
            auth_required=True,
        ),
    ]

    docs = DocsLinks(
        swagger=_api_link(
            base_url,
            name="Swagger UI",
            method="GET",
            path="/docs",
            description="Interactive API explorer for testing endpoints.",
        ),
        redoc=_api_link(
            base_url,
            name="ReDoc",
            method="GET",
            path="/redoc",
            description="Readable API reference documentation.",
        ),
        openapi=_api_link(
            base_url,
            name="OpenAPI Schema",
            method="GET",
            path="/openapi.json",
            description="Machine-readable OpenAPI 3 schema.",
        ),
    )

    connectivity = ConnectivitySummary(
        overall_status=system_info["status"],
        supabase_connected=system_info["supabase"]["connected"],
        supabase_url=system_info["supabase"]["url"],
        supabase_project_ref=system_info["supabase"]["project_ref"],
        storage_connected=system_info["storage"]["connected"],
        default_bucket=system_info["storage"]["default_bucket"],
        default_bucket_exists=system_info["storage"]["default_bucket_exists"],
        total_buckets=system_info["storage"]["total_buckets"],
    )

    return RootResponse(
        name=settings.app_name,
        description=API_DESCRIPTION,
        version=API_VERSION,
        status="running",
        environment=settings.app_env,
        base_url=base_url.rstrip("/"),
        docs=docs,
        connectivity=connectivity,
        settings=SettingsInfo(**system_info["settings"]),
        links=links,
        detailed_status_url=_absolute_url(base_url, "/info"),
    )
