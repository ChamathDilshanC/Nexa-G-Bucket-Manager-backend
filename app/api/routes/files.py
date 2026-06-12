"""File listing and delete endpoints.

Author: Chamath Dilshan
"""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_bucket_registry, get_storage_service, get_user_context
from app.schemas.files import FileListResponse
from app.services.bucket_registry import BucketRegistry
from app.services.supabase_storage import SupabaseStorageService

router = APIRouter(prefix="/buckets", tags=["files"])


@router.get("/{bucket_name}/files", response_model=list[FileListResponse])
def list_files(
    bucket_name: str,
    prefix: str | None = None,
    user: dict = Depends(get_user_context),
    storage: SupabaseStorageService = Depends(get_storage_service),
    registry: BucketRegistry = Depends(get_bucket_registry),
) -> list[FileListResponse]:
    """List files in a user-owned bucket."""
    registry.require_bucket_access(user["user_id"], bucket_name)
    files = storage.list_files(bucket_name=bucket_name, prefix=prefix)
    return [FileListResponse(**item) for item in files]


@router.delete("/{bucket_name}/files/{object_path:path}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    bucket_name: str,
    object_path: str,
    user: dict = Depends(get_user_context),
    storage: SupabaseStorageService = Depends(get_storage_service),
    registry: BucketRegistry = Depends(get_bucket_registry),
) -> None:
    """Delete a single file object from a user-owned bucket."""
    registry.require_bucket_access(user["user_id"], bucket_name)
    storage.delete_file(bucket_name=bucket_name, object_path=object_path)
