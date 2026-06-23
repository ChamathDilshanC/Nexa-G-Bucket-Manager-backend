"""Bucket share link management.

Author: Chamath Dilshan
"""

import secrets
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status

from app.services.bucket_registry import BucketRegistry
from app.services.supabase_client import get_supabase_admin_client


class ShareService:
    """Create and validate shareable bucket links."""

    TABLE = "bucket_share_links"

    def __init__(self) -> None:
        self.client = get_supabase_admin_client()
        self.registry = BucketRegistry()

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def build_share_url(token: str) -> str:
        return f"nexagbucket://share/{token}"

    def _require_owner(self, user_id: str, bucket_name: str) -> dict[str, Any]:
        if not self.registry.user_owns_bucket(user_id, bucket_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this bucket.",
            )
        owned = next(
            (
                item
                for item in self.registry.list_user_buckets(user_id)
                if item["bucket_name"] == bucket_name
            ),
            None,
        )
        if not owned:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bucket not found.",
            )
        return owned

    def _to_response(self, row: dict[str, Any], display_name: str | None = None) -> dict[str, Any]:
        return {
            "id": row["id"],
            "bucket_name": row["bucket_name"],
            "display_name": display_name,
            "token": row["token"],
            "role": row["role"],
            "anyone_with_link": row["anyone_with_link"],
            "share_url": self.build_share_url(row["token"]),
            "revoked_at": row.get("revoked_at"),
            "expires_at": row.get("expires_at"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _active_filter(self, query: Any) -> Any:
        return query.is_("revoked_at", "null")

    def create_share(
        self,
        user_id: str,
        bucket_name: str,
        *,
        role: str = "viewer",
        anyone_with_link: bool = True,
    ) -> dict[str, Any]:
        owned = self._require_owner(user_id, bucket_name)

        existing = (
            self.client.table(self.TABLE)
            .select("*")
            .eq("bucket_name", bucket_name)
            .eq("created_by", user_id)
            .is_("revoked_at", "null")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if existing.data:
            row = existing.data[0]
            updated = (
                self.client.table(self.TABLE)
                .update(
                    {
                        "role": role,
                        "anyone_with_link": anyone_with_link,
                        "updated_at": self._now_iso(),
                    }
                )
                .eq("id", row["id"])
                .execute()
            )
            return self._to_response(updated.data[0], owned["display_name"])

        token = secrets.token_urlsafe(24)
        inserted = (
            self.client.table(self.TABLE)
            .insert(
                {
                    "bucket_name": bucket_name,
                    "created_by": user_id,
                    "token": token,
                    "role": role,
                    "anyone_with_link": anyone_with_link,
                }
            )
            .execute()
        )
        return self._to_response(inserted.data[0], owned["display_name"])

    def list_bucket_shares(self, user_id: str, bucket_name: str) -> list[dict[str, Any]]:
        owned = self._require_owner(user_id, bucket_name)
        response = (
            self.client.table(self.TABLE)
            .select("*")
            .eq("bucket_name", bucket_name)
            .eq("created_by", user_id)
            .is_("revoked_at", "null")
            .order("created_at", desc=True)
            .execute()
        )
        return [self._to_response(row, owned["display_name"]) for row in response.data]

    def list_user_shares(self, user_id: str) -> list[dict[str, Any]]:
        response = (
            self.client.table(self.TABLE)
            .select("*")
            .eq("created_by", user_id)
            .is_("revoked_at", "null")
            .order("created_at", desc=True)
            .execute()
        )
        shares: list[dict[str, Any]] = []
        buckets = {item["bucket_name"]: item["display_name"] for item in self.registry.list_user_buckets(user_id)}
        for row in response.data:
            shares.append(self._to_response(row, buckets.get(row["bucket_name"])))
        return shares

    def update_share(
        self,
        user_id: str,
        bucket_name: str,
        share_id: str,
        *,
        role: str | None = None,
        anyone_with_link: bool | None = None,
    ) -> dict[str, Any]:
        owned = self._require_owner(user_id, bucket_name)
        updates: dict[str, Any] = {"updated_at": self._now_iso()}
        if role is not None:
            updates["role"] = role
        if anyone_with_link is not None:
            updates["anyone_with_link"] = anyone_with_link

        response = (
            self.client.table(self.TABLE)
            .update(updates)
            .eq("id", share_id)
            .eq("bucket_name", bucket_name)
            .eq("created_by", user_id)
            .is_("revoked_at", "null")
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share link not found.")
        return self._to_response(response.data[0], owned["display_name"])

    def revoke_share(self, user_id: str, bucket_name: str, share_id: str) -> None:
        self._require_owner(user_id, bucket_name)
        response = (
            self.client.table(self.TABLE)
            .update({"revoked_at": self._now_iso(), "updated_at": self._now_iso()})
            .eq("id", share_id)
            .eq("bucket_name", bucket_name)
            .eq("created_by", user_id)
            .is_("revoked_at", "null")
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share link not found.")

    def resolve_token(self, token: str) -> dict[str, Any]:
        response = (
            self.client.table(self.TABLE)
            .select("*")
            .eq("token", token)
            .is_("revoked_at", "null")
            .limit(1)
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share link not found or expired.")

        row = response.data[0]
        if not row.get("anyone_with_link"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This share link is restricted.")

        expires_at = row.get("expires_at")
        if expires_at:
            expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if expiry < datetime.now(UTC):
                raise HTTPException(status_code=status.HTTP_410_GONE, detail="Share link has expired.")

        owned = (
            self.client.table(BucketRegistry.TABLE)
            .select("display_name")
            .eq("bucket_name", row["bucket_name"])
            .limit(1)
            .execute()
        )
        display_name = owned.data[0]["display_name"] if owned.data else row["bucket_name"]
        return {
            "row": row,
            "bucket_name": row["bucket_name"],
            "display_name": display_name,
            "role": row["role"],
        }
