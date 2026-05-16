"""Bucket API schemas.

Author: Chamath Dilshan
"""

from pydantic import BaseModel, Field


class BucketCreateRequest(BaseModel):
    """Payload required to create a new bucket."""

    name: str = Field(min_length=3, max_length=63)
    location: str = "US"


class BucketUpdateRequest(BaseModel):
    """Payload for updating mutable bucket metadata."""

    storage_class: str = Field(min_length=2, max_length=32)


class BucketResponse(BaseModel):
    """Standardized bucket metadata response model."""

    name: str
    location: str | None = None
    storage_class: str | None = None
