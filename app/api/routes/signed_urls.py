"""Signed URL generation endpoints.

Author: Chamath Dilshan
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_storage_service
from app.core.config import get_settings
from app.schemas.files import (
    DownloadSignedURLRequest,
    SignedURLResponse,
    UploadSignedURLRequest,
)
from app.services.gcp_storage import GCPStorageService

router = APIRouter(prefix="/files", tags=["signed-urls"])


@router.post("/upload-url", response_model=SignedURLResponse)
def create_upload_signed_url(
    payload: UploadSignedURLRequest,
    current_user: dict = Depends(get_current_user),
    storage: GCPStorageService = Depends(get_storage_service),
) -> SignedURLResponse:
    """Issue a signed upload URL with mime type validation."""
    _ = current_user
    settings = get_settings()
    if payload.content_type not in settings.parsed_allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported MIME type. Allowed: {sorted(settings.parsed_allowed_mime_types)}",
        )

    url = storage.generate_upload_signed_url(
        bucket_name=payload.bucket,
        object_path=payload.path,
        content_type=payload.content_type,
    )
    return SignedURLResponse(url=url, expires_in=settings.signed_url_expiry_seconds)


@router.post("/download-url", response_model=SignedURLResponse)
def create_download_signed_url(
    payload: DownloadSignedURLRequest,
    current_user: dict = Depends(get_current_user),
    storage: GCPStorageService = Depends(get_storage_service),
) -> SignedURLResponse:
    """Issue a signed download URL for the given object path."""
    _ = current_user
    settings = get_settings()
    url = storage.generate_download_signed_url(bucket_name=payload.bucket, object_path=payload.path)
    return SignedURLResponse(url=url, expires_in=settings.signed_url_expiry_seconds)
