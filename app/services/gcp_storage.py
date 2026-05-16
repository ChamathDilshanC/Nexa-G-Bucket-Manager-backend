"""Google Cloud Storage service abstraction.

Author: Chamath Dilshan
"""

import json
from typing import Any

from google.cloud import storage
from google.oauth2 import service_account

from app.core.config import get_settings


class GCPStorageService:
    """Encapsulates bucket and file operations for GCP Storage."""

    def __init__(self) -> None:
        """Initialize the storage client using service account JSON."""
        settings = get_settings()
        if not settings.gcp_project_id or not settings.gcp_service_account_json:
            raise ValueError("GCP_PROJECT_ID and GCP_SERVICE_ACCOUNT_JSON must be configured.")
        service_account_info = json.loads(settings.gcp_service_account_json)
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        self.client = storage.Client(project=settings.gcp_project_id, credentials=credentials)
        self.settings = settings

    def list_buckets(self) -> list[dict[str, Any]]:
        """Return all buckets visible to the configured service account."""
        buckets: list[dict[str, Any]] = []
        for bucket in self.client.list_buckets():
            buckets.append(
                {
                    "name": bucket.name,
                    "location": bucket.location,
                    "storage_class": bucket.storage_class,
                    "time_created": bucket.time_created,
                }
            )
        return buckets

    def create_bucket(self, name: str, location: str = "US") -> dict[str, Any]:
        """Create a new storage bucket and return metadata."""
        bucket = self.client.bucket(name)
        created = self.client.create_bucket(bucket, location=location)
        return {
            "name": created.name,
            "location": created.location,
            "storage_class": created.storage_class,
            "time_created": created.time_created,
        }

    def update_bucket(self, name: str, storage_class: str) -> dict[str, Any]:
        """Update mutable bucket metadata such as storage class."""
        bucket = self.client.get_bucket(name)
        bucket.storage_class = storage_class
        updated = bucket.patch()
        return {
            "name": updated.name,
            "location": updated.location,
            "storage_class": updated.storage_class,
        }

    def delete_bucket(self, name: str, force: bool = False) -> None:
        """Delete a bucket with optional recursive object cleanup."""
        bucket = self.client.bucket(name)
        if force:
            for blob in bucket.list_blobs():
                blob.delete()
        bucket.delete()

    def list_files(self, bucket_name: str, prefix: str | None = None) -> list[dict[str, Any]]:
        """List files in a bucket with optional path prefix filtering."""
        blobs = self.client.list_blobs(bucket_name, prefix=prefix)
        return [
            {
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "updated": blob.updated,
            }
            for blob in blobs
        ]

    def delete_file(self, bucket_name: str, object_path: str) -> None:
        """Delete a single object from the specified bucket."""
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(object_path)
        blob.delete()

    def generate_upload_signed_url(self, bucket_name: str, object_path: str, content_type: str) -> str:
        """Create a short-lived signed URL for direct uploads."""
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(object_path)
        return blob.generate_signed_url(
            version="v4",
            expiration=self.settings.signed_url_expiry_seconds,
            method="PUT",
            content_type=content_type,
        )

    def generate_download_signed_url(self, bucket_name: str, object_path: str) -> str:
        """Create a short-lived signed URL for file downloads."""
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(object_path)
        return blob.generate_signed_url(
            version="v4",
            expiration=self.settings.signed_url_expiry_seconds,
            method="GET",
        )
