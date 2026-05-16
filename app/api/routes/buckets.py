"""Bucket management endpoints.

Author: Chamath Dilshan
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_storage_service
from app.schemas.buckets import BucketCreateRequest, BucketResponse, BucketUpdateRequest
from app.services.gcp_storage import GCPStorageService

router = APIRouter(prefix="/buckets", tags=["buckets"])


@router.get("", response_model=list[BucketResponse])
def list_buckets(
    current_user: dict = Depends(get_current_user),
    storage: GCPStorageService = Depends(get_storage_service),
) -> list[BucketResponse]:
    """List buckets available to the authenticated principal."""
    _ = current_user
    buckets = storage.list_buckets()
    return [BucketResponse(**bucket) for bucket in buckets]


@router.post("", response_model=BucketResponse, status_code=status.HTTP_201_CREATED)
def create_bucket(
    payload: BucketCreateRequest,
    current_user: dict = Depends(get_current_user),
    storage: GCPStorageService = Depends(get_storage_service),
) -> BucketResponse:
    """Create a bucket after token verification."""
    _ = current_user
    created = storage.create_bucket(name=payload.name, location=payload.location)
    return BucketResponse(**created)


@router.patch("/{bucket_name}", response_model=BucketResponse)
def update_bucket(
    bucket_name: str,
    payload: BucketUpdateRequest,
    current_user: dict = Depends(get_current_user),
    storage: GCPStorageService = Depends(get_storage_service),
) -> BucketResponse:
    """Update safe bucket metadata fields."""
    _ = current_user
    updated = storage.update_bucket(name=bucket_name, storage_class=payload.storage_class)
    return BucketResponse(**updated)


@router.delete("/{bucket_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bucket(
    bucket_name: str,
    force: bool = False,
    current_user: dict = Depends(get_current_user),
    storage: GCPStorageService = Depends(get_storage_service),
) -> None:
    """Delete bucket and optionally its objects."""
    _ = current_user
    try:
        storage.delete_bucket(name=bucket_name, force=force)
    except Exception as exc:  # pragma: no cover - provider-specific failures
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to delete bucket: {exc}",
        ) from exc
