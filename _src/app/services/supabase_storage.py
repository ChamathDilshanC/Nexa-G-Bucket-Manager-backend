"""Supabase Storage service abstraction.

Author: Chamath Dilshan
"""

from datetime import datetime
from typing import Any

from app.core.config import get_settings
from app.services.supabase_client import get_supabase_admin_client


class SupabaseStorageService:
    """Encapsulates bucket and file operations for Supabase Storage."""

    def __init__(self) -> None:
        """Initialize the storage client using the Supabase service role key."""
        settings = get_settings()
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured.")
        self.client = get_supabase_admin_client()
        self.settings = settings

    def list_buckets(self) -> list[dict[str, Any]]:
        """Return all storage buckets in the Supabase project."""
        return [self._bucket_to_dict(bucket) for bucket in self.client.storage.list_buckets()]

    def get_bucket(self, name: str) -> dict[str, Any]:
        """Return metadata for a single storage bucket."""
        bucket = self.client.storage.get_bucket(name)
        return self._bucket_to_dict(bucket)

    def create_bucket(
        self,
        name: str,
        public: bool = False,
        allowed_mime_types: list[str] | None = None,
        file_size_limit: int | None = None,
    ) -> dict[str, Any]:
        """Create a new storage bucket and return metadata."""
        options: dict[str, Any] = {"public": public}
        if allowed_mime_types is not None:
            options["allowed_mime_types"] = allowed_mime_types
        if file_size_limit is not None:
            options["file_size_limit"] = file_size_limit

        self.client.storage.create_bucket(name, options=options)
        bucket = self.client.storage.get_bucket(name)
        return self._bucket_to_dict(bucket)

    def update_bucket(
        self,
        name: str,
        public: bool | None = None,
        allowed_mime_types: list[str] | None = None,
        file_size_limit: int | None = None,
    ) -> dict[str, Any]:
        """Update mutable bucket settings."""
        options: dict[str, Any] = {}
        if public is not None:
            options["public"] = public
        if allowed_mime_types is not None:
            options["allowed_mime_types"] = allowed_mime_types
        if file_size_limit is not None:
            options["file_size_limit"] = file_size_limit

        if not options:
            bucket = self.client.storage.get_bucket(name)
            return self._bucket_to_dict(bucket)

        self.client.storage.update_bucket(name, options=options)
        bucket = self.client.storage.get_bucket(name)
        return self._bucket_to_dict(bucket)

    def delete_bucket(self, name: str, force: bool = False) -> None:
        """Delete a bucket, optionally emptying it first."""
        if force:
            self.client.storage.empty_bucket(name)
        self.client.storage.delete_bucket(name)

    def list_files(self, bucket_name: str, prefix: str | None = None) -> list[dict[str, Any]]:
        """List files in a bucket, including nested folders."""

        def walk(folder_path: str) -> list[dict[str, Any]]:
            items = self.client.storage.from_(bucket_name).list(path=folder_path)
            files: list[dict[str, Any]] = []

            for item in items:
                name = item.get("name")
                if not name:
                    continue

                metadata = item.get("metadata") or {}
                full_path = f"{folder_path}/{name}" if folder_path else name
                is_folder = metadata.get("size") is None and item.get("id") is None

                if is_folder:
                    files.extend(walk(full_path))
                    continue

                files.append(
                    {
                        "name": full_path,
                        "size": metadata.get("size"),
                        "content_type": metadata.get("mimetype"),
                        "updated": item.get("updated_at"),
                    }
                )

            return files

        root = (prefix or "").strip("/")
        return walk(root)

    def delete_file(self, bucket_name: str, object_path: str) -> None:
        """Delete a single object from the specified bucket."""
        self.client.storage.from_(bucket_name).remove([object_path])

    def generate_upload_signed_url(
        self, bucket_name: str, object_path: str, content_type: str
    ) -> dict[str, str]:
        """Create a short-lived signed URL for direct uploads."""
        _ = content_type
        result = self.client.storage.from_(bucket_name).create_signed_upload_url(object_path)
        return {
            "url": result.get("signedUrl") or result.get("signed_url") or "",
            "token": result.get("token") or "",
        }

    def generate_download_signed_url(self, bucket_name: str, object_path: str) -> str:
        """Create a short-lived signed URL for file downloads."""
        result = self.client.storage.from_(bucket_name).create_signed_url(
            object_path,
            self.settings.signed_url_expiry_seconds,
        )
        return result.get("signedUrl") or result.get("signedURL") or ""

    @staticmethod
    def _bucket_to_dict(bucket: Any) -> dict[str, Any]:
        """Normalize Supabase bucket models into API-friendly dictionaries."""
        created_at = getattr(bucket, "created_at", None)
        updated_at = getattr(bucket, "updated_at", None)
        return {
            "name": bucket.name,
            "public": bucket.public,
            "file_size_limit": bucket.file_size_limit,
            "allowed_mime_types": bucket.allowed_mime_types,
            "created_at": created_at.isoformat() if isinstance(created_at, datetime) else created_at,
            "updated_at": updated_at.isoformat() if isinstance(updated_at, datetime) else updated_at,
        }
