"""File and signed URL schemas.

Author: Chamath Dilshan
"""

from pydantic import BaseModel, Field


class FileListResponse(BaseModel):
    """Represents file metadata in list operations."""

    name: str
    size: int | None = None
    content_type: str | None = None


class UploadSignedURLRequest(BaseModel):
    """Payload to request a signed URL for uploading an object."""

    bucket: str = Field(min_length=3, max_length=63)
    path: str = Field(min_length=1)
    content_type: str = Field(min_length=3, max_length=128)


class DownloadSignedURLRequest(BaseModel):
    """Payload to request a signed URL for downloading an object."""

    bucket: str = Field(min_length=3, max_length=63)
    path: str = Field(min_length=1)


class SignedURLResponse(BaseModel):
    """Unified signed URL response payload."""

    url: str
    expires_in: int
