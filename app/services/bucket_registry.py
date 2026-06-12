"""Per-user bucket ownership registry backed by Supabase Postgres.

Author: Chamath Dilshan
"""

import re
from typing import Any

from fastapi import HTTPException, status

from app.services.supabase_client import get_supabase_admin_client

_BUCKET_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$")


class BucketRegistry:
    """Tracks which storage buckets belong to which authenticated users."""

    TABLE = "user_buckets"

    def __init__(self) -> None:
        self.client = get_supabase_admin_client()

    @staticmethod
    def build_storage_bucket_name(user_id: str, display_name: str) -> str:
        """Create a unique storage bucket id for a user-owned bucket."""
        slug = display_name.lower().strip().replace("_", "-")
        slug = re.sub(r"[^a-z0-9-]", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        if len(slug) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bucket name must contain at least 3 valid characters.",
            )

        prefix = f"u{user_id.replace('-', '')[:10]}"
        bucket_name = f"{prefix}-{slug}"[:63].strip("-")
        if not _BUCKET_NAME_PATTERN.match(bucket_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bucket name could not be normalized to a valid storage bucket id.",
            )
        return bucket_name

    def register_bucket(self, user_id: str, bucket_name: str, display_name: str) -> dict[str, Any]:
        """Persist ownership for a newly created storage bucket."""
        response = (
            self.client.table(self.TABLE)
            .insert(
                {
                    "user_id": user_id,
                    "bucket_name": bucket_name,
                    "display_name": display_name,
                }
            )
            .execute()
        )
        return response.data[0]

    def list_user_buckets(self, user_id: str) -> list[dict[str, Any]]:
        """Return all bucket ownership rows for the given user."""
        response = (
            self.client.table(self.TABLE)
            .select("bucket_name,display_name,created_at")
            .eq("user_id", user_id)
            .order("created_at")
            .execute()
        )
        return response.data

    def user_owns_bucket(self, user_id: str, bucket_name: str) -> bool:
        """Check whether the user owns the requested storage bucket."""
        response = (
            self.client.table(self.TABLE)
            .select("bucket_name")
            .eq("user_id", user_id)
            .eq("bucket_name", bucket_name)
            .limit(1)
            .execute()
        )
        return bool(response.data)

    def remove_bucket(self, user_id: str, bucket_name: str) -> None:
        """Delete the ownership record for a bucket."""
        if not self.user_owns_bucket(user_id, bucket_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bucket not found for the authenticated user.",
            )
        self.client.table(self.TABLE).delete().eq("user_id", user_id).eq("bucket_name", bucket_name).execute()

    def require_bucket_access(self, user_id: str, bucket_name: str) -> None:
        """Raise when the authenticated user does not own the bucket."""
        if not self.user_owns_bucket(user_id, bucket_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this bucket.",
            )
