"""Signed URL generation endpoints.

Author: Chamath Dilshan
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_bucket_registry, get_storage_service, get_user_context
from app.core.config import get_settings
from app.schemas.files import (
    DownloadSignedURLRequest,
    SignedURLResponse,
    UploadSignedURLRequest,
)
from app.services.bucket_registry import BucketRegistry
from app.services.supabase_storage import SupabaseStorageService

router = APIRouter(prefix="/files", tags=["signed-urls"])


@router.post("/upload-url", response_model=SignedURLResponse)
def create_upload_signed_url(
    payload: UploadSignedURLRequest,
    user: dict = Depends(get_user_context),
    storage: SupabaseStorageService = Depends(get_storage_service),
    registry: BucketRegistry = Depends(get_bucket_registry),
) -> SignedURLResponse:
    """Issue a signed upload URL for a user-owned bucket."""
    settings = get_settings()
    registry.require_bucket_access(user["user_id"], payload.bucket)

    if payload.content_type not in settings.parsed_allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported MIME type. Allowed: {sorted(settings.parsed_allowed_mime_types)}",
        )

    max_upload_bytes = settings.max_upload_size_mb * 1024 * 1024
    if payload.file_size_bytes is not None and payload.file_size_bytes > max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds the maximum upload size of {settings.max_upload_size_mb} MB.",
        )

    signed = storage.generate_upload_signed_url(
        bucket_name=payload.bucket,
        object_path=payload.path,
        content_type=payload.content_type,
    )
    return SignedURLResponse(
        url=signed["url"],
        token=signed["token"],
        expires_in=settings.signed_url_expiry_seconds,
    )


@router.post("/download-url", response_model=SignedURLResponse)
def create_download_signed_url(
    payload: DownloadSignedURLRequest,
    user: dict = Depends(get_user_context),
    storage: SupabaseStorageService = Depends(get_storage_service),
    registry: BucketRegistry = Depends(get_bucket_registry),
) -> SignedURLResponse:
    """Issue a signed download URL for a user-owned bucket object."""
    settings = get_settings()
    registry.require_bucket_access(user["user_id"], payload.bucket)
    url = storage.generate_download_signed_url(bucket_name=payload.bucket, object_path=payload.path)
    return SignedURLResponse(url=url, expires_in=settings.signed_url_expiry_seconds)
