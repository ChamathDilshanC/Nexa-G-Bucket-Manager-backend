"""Share link management and public token access.

Author: Chamath Dilshan
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_storage_service, get_user_context
from app.schemas.files import FileListResponse, SignedURLResponse
from app.schemas.shares import (
    ShareCreateRequest,
    ShareDownloadRequest,
    ShareLinkResponse,
    ShareResolveResponse,
    ShareUpdateRequest,
)
from app.services.share_service import ShareService
from app.services.supabase_storage import SupabaseStorageService

router = APIRouter(tags=["shares"])


def get_share_service() -> ShareService:
    return ShareService()


@router.get("/shares/mine", response_model=list[ShareLinkResponse])
def list_my_shares(
    user: dict = Depends(get_user_context),
    shares: ShareService = Depends(get_share_service),
) -> list[ShareLinkResponse]:
    """List active share links created by the authenticated user."""
    return shares.list_user_shares(user["user_id"])


@router.post("/buckets/{bucket_name}/shares", response_model=ShareLinkResponse, status_code=201)
def create_bucket_share(
    bucket_name: str,
    payload: ShareCreateRequest,
    user: dict = Depends(get_user_context),
    shares: ShareService = Depends(get_share_service),
) -> ShareLinkResponse:
    """Create or refresh a share link for a bucket."""
    return shares.create_share(
        user["user_id"],
        bucket_name,
        role=payload.role,
        anyone_with_link=payload.anyone_with_link,
    )


@router.get("/buckets/{bucket_name}/shares", response_model=list[ShareLinkResponse])
def list_bucket_shares(
    bucket_name: str,
    user: dict = Depends(get_user_context),
    shares: ShareService = Depends(get_share_service),
) -> list[ShareLinkResponse]:
    """List active share links for a bucket."""
    return shares.list_bucket_shares(user["user_id"], bucket_name)


@router.patch("/buckets/{bucket_name}/shares/{share_id}", response_model=ShareLinkResponse)
def update_bucket_share(
    bucket_name: str,
    share_id: str,
    payload: ShareUpdateRequest,
    user: dict = Depends(get_user_context),
    shares: ShareService = Depends(get_share_service),
) -> ShareLinkResponse:
    """Update role or access mode for a share link."""
    return shares.update_share(
        user["user_id"],
        bucket_name,
        share_id,
        role=payload.role,
        anyone_with_link=payload.anyone_with_link,
    )


@router.delete("/buckets/{bucket_name}/shares/{share_id}", status_code=204)
def revoke_bucket_share(
    bucket_name: str,
    share_id: str,
    user: dict = Depends(get_user_context),
    shares: ShareService = Depends(get_share_service),
) -> None:
    """Revoke a share link."""
    shares.revoke_share(user["user_id"], bucket_name, share_id)


@router.get("/shares/{token}", response_model=ShareResolveResponse)
def resolve_share(
    token: str,
    shares: ShareService = Depends(get_share_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
) -> ShareResolveResponse:
    """Resolve a public share token to bucket metadata."""
    resolved = shares.resolve_token(token)
    file_count = storage.count_files(resolved["bucket_name"])
    return ShareResolveResponse(
        bucket_name=resolved["bucket_name"],
        display_name=resolved["display_name"],
        role=resolved["role"],
        file_count=file_count,
    )


@router.get("/shares/{token}/files", response_model=list[FileListResponse])
def list_shared_files(
    token: str,
    prefix: str | None = None,
    shares: ShareService = Depends(get_share_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
) -> list[FileListResponse]:
    """List files in a bucket using a share token."""
    resolved = shares.resolve_token(token)
    files = storage.list_files(bucket_name=resolved["bucket_name"], prefix=prefix)
    return [FileListResponse(**item) for item in files]


@router.post("/shares/{token}/download-url", response_model=SignedURLResponse)
def create_shared_download_url(
    token: str,
    payload: ShareDownloadRequest,
    shares: ShareService = Depends(get_share_service),
    storage: SupabaseStorageService = Depends(get_storage_service),
) -> SignedURLResponse:
    """Issue a signed download URL using a share token."""
    from app.core.config import get_settings

    resolved = shares.resolve_token(token)
    settings = get_settings()
    url = storage.generate_download_signed_url(
        bucket_name=resolved["bucket_name"],
        object_path=payload.path,
    )
    return SignedURLResponse(url=url, expires_in=settings.signed_url_expiry_seconds)
