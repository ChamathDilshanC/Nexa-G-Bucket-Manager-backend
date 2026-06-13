"""Bucket API schemas.

Author: Chamath Dilshan
"""

from pydantic import BaseModel, Field


class BucketCreateRequest(BaseModel):
    """Payload required to create a new bucket."""

    name: str = Field(min_length=3, max_length=63)
    public: bool = False
    allowed_mime_types: list[str] | None = None
    file_size_limit: int | None = Field(default=None, gt=0)


class BucketUpdateRequest(BaseModel):
    """Payload for updating mutable bucket settings."""

    public: bool | None = None
    allowed_mime_types: list[str] | None = None
    file_size_limit: int | None = Field(default=None, gt=0)


class BucketResponse(BaseModel):
    """Standardized bucket metadata response model."""

    name: str
    display_name: str | None = None
    public: bool | None = None
    file_size_limit: int | None = None
    allowed_mime_types: list[str] | None = None
    file_count: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
