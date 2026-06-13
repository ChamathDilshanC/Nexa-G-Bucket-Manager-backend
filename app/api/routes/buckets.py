"""Bucket management endpoints.

Author: Chamath Dilshan
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_bucket_registry, get_storage_service, get_user_context
from app.schemas.buckets import BucketCreateRequest, BucketResponse, BucketUpdateRequest
from app.services.bucket_registry import BucketRegistry
from app.services.supabase_storage import SupabaseStorageService

router = APIRouter(prefix="/buckets", tags=["buckets"])


def _to_bucket_response(
    storage_bucket: dict,
    *,
    display_name: str | None = None,
    created_at: str | None = None,
    file_count: int | None = None,
) -> BucketResponse:
    """Merge storage metadata with registry metadata."""
    return BucketResponse(
        name=storage_bucket["name"],
        display_name=display_name,
        public=storage_bucket.get("public"),
        file_size_limit=storage_bucket.get("file_size_limit"),
        allowed_mime_types=storage_bucket.get("allowed_mime_types"),
        file_count=file_count,
        created_at=created_at or storage_bucket.get("created_at"),
        updated_at=storage_bucket.get("updated_at"),
    )


@router.get("", response_model=list[BucketResponse])
def list_buckets(
    user: dict = Depends(get_user_context),
    storage: SupabaseStorageService = Depends(get_storage_service),
    registry: BucketRegistry = Depends(get_bucket_registry),
) -> list[BucketResponse]:
    """List buckets owned by the authenticated user."""
    owned_buckets = registry.list_user_buckets(user["user_id"])
    responses: list[BucketResponse] = []

    for owned in owned_buckets:
        try:
            metadata = storage.get_bucket(owned["bucket_name"])
            file_count = storage.count_files(owned["bucket_name"])
            responses.append(
                _to_bucket_response(
                    metadata,
                    display_name=owned["display_name"],
                    created_at=owned.get("created_at"),
                    file_count=file_count,
                )
            )
        except Exception:  # pragma: no cover - provider-specific failures
            responses.append(
                BucketResponse(
                    name=owned["bucket_name"],
                    display_name=owned["display_name"],
                    created_at=owned.get("created_at"),
                    file_count=0,
                )
            )

    return responses


@router.post("", response_model=BucketResponse, status_code=status.HTTP_201_CREATED)
def create_bucket(
    payload: BucketCreateRequest,
    user: dict = Depends(get_user_context),
    storage: SupabaseStorageService = Depends(get_storage_service),
    registry: BucketRegistry = Depends(get_bucket_registry),
) -> BucketResponse:
    """Create a user-owned bucket. One user can create multiple buckets."""
    bucket_name = registry.build_storage_bucket_name(user["user_id"], payload.name)

    try:
        created = storage.create_bucket(
            name=bucket_name,
            public=payload.public,
            allowed_mime_types=payload.allowed_mime_types,
            file_size_limit=payload.file_size_limit,
        )
        owned = registry.register_bucket(
            user_id=user["user_id"],
            bucket_name=bucket_name,
            display_name=payload.name,
        )
    except Exception as exc:
        if "duplicate key value" in str(exc).lower() or "already exists" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A bucket with this name already exists for your account.",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to create bucket: {exc}",
        ) from exc

    return _to_bucket_response(
        created,
        display_name=owned["display_name"],
        created_at=owned.get("created_at"),
    )


@router.patch("/{bucket_name}", response_model=BucketResponse)
def update_bucket(
    bucket_name: str,
    payload: BucketUpdateRequest,
    user: dict = Depends(get_user_context),
    storage: SupabaseStorageService = Depends(get_storage_service),
    registry: BucketRegistry = Depends(get_bucket_registry),
) -> BucketResponse:
    """Update safe bucket settings for a user-owned bucket."""
    registry.require_bucket_access(user["user_id"], bucket_name)
    owned = next(
        (
            item
            for item in registry.list_user_buckets(user["user_id"])
            if item["bucket_name"] == bucket_name
        ),
        None,
    )
    updated = storage.update_bucket(
        name=bucket_name,
        public=payload.public,
        allowed_mime_types=payload.allowed_mime_types,
        file_size_limit=payload.file_size_limit,
    )
    return _to_bucket_response(
        updated,
        display_name=owned["display_name"] if owned else None,
        created_at=owned.get("created_at") if owned else None,
    )


@router.delete("/{bucket_name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bucket(
    bucket_name: str,
    force: bool = False,
    user: dict = Depends(get_user_context),
    storage: SupabaseStorageService = Depends(get_storage_service),
    registry: BucketRegistry = Depends(get_bucket_registry),
) -> None:
    """Delete a user-owned bucket and optionally its objects."""
    registry.require_bucket_access(user["user_id"], bucket_name)
    try:
        storage.delete_bucket(name=bucket_name, force=force)
        registry.remove_bucket(user["user_id"], bucket_name)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - provider-specific failures
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to delete bucket: {exc}",
        ) from exc
