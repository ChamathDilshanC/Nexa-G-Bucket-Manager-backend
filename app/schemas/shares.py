"""Share link request and response models.

Author: Chamath Dilshan
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ShareRole = Literal["viewer", "editor"]


class ShareCreateRequest(BaseModel):
    """Create or refresh a share link for a bucket."""

    role: ShareRole = "viewer"
    anyone_with_link: bool = True


class ShareUpdateRequest(BaseModel):
    """Update an existing share link."""

    role: ShareRole | None = None
    anyone_with_link: bool | None = None


class ShareLinkResponse(BaseModel):
    """Share link metadata returned to clients."""

    id: str
    bucket_name: str
    display_name: str | None = None
    token: str
    role: ShareRole
    anyone_with_link: bool
    share_url: str
    revoked_at: datetime | None = None
    expires_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ShareResolveResponse(BaseModel):
    """Public metadata for a resolved share token."""

    bucket_name: str
    display_name: str
    role: ShareRole
    file_count: int | None = None


class ShareDownloadRequest(BaseModel):
    """Download request for a shared object."""

    path: str = Field(min_length=1)
