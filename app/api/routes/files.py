"""File listing and delete endpoints.

Author: Chamath Dilshan
"""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_storage_service
from app.schemas.files import FileListResponse
from app.services.gcp_storage import GCPStorageService

router = APIRouter(prefix="/buckets", tags=["files"])


@router.get("/{bucket_name}/files", response_model=list[FileListResponse])
def list_files(
    bucket_name: str,
    prefix: str | None = None,
    current_user: dict = Depends(get_current_user),
    storage: GCPStorageService = Depends(get_storage_service),
) -> list[FileListResponse]:
    """List files in a bucket for the authenticated user."""
    _ = current_user
    files = storage.list_files(bucket_name=bucket_name, prefix=prefix)
    return [FileListResponse(**item) for item in files]


@router.delete("/{bucket_name}/files/{object_path:path}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    bucket_name: str,
    object_path: str,
    current_user: dict = Depends(get_current_user),
    storage: GCPStorageService = Depends(get_storage_service),
) -> None:
    """Delete a single file object from the specified bucket."""
    _ = current_user
    storage.delete_file(bucket_name=bucket_name, object_path=object_path)
