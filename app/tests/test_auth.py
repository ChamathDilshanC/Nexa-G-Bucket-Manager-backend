"""Authentication helper tests.

Author: Chamath Dilshan
"""

from app.core.security import build_user_context
from app.services.bucket_registry import BucketRegistry


def test_build_user_context_from_google_jwt_claims() -> None:
    """Verify JWT claims are normalized into a user context."""
    payload = {
        "sub": "11111111-2222-3333-4444-555555555555",
        "email": "user@example.com",
        "role": "authenticated",
        "app_metadata": {"provider": "google"},
    }

    context = build_user_context(payload)

    assert context["user_id"] == payload["sub"]
    assert context["email"] == "user@example.com"
    assert context["provider"] == "google"
    assert context["is_google_user"] is True


def test_build_storage_bucket_name_is_unique_per_user() -> None:
    """Verify user bucket names are namespaced to avoid collisions."""
    user_a = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    user_b = "ffffffff-bbbb-cccc-dddd-eeeeeeeeeeee"

    bucket_a = BucketRegistry.build_storage_bucket_name(user_a, "photos")
    bucket_b = BucketRegistry.build_storage_bucket_name(user_b, "photos")

    assert bucket_a != bucket_b
    assert bucket_a == "uaaaaaaaabb-photos"
    assert bucket_b == "uffffffffbb-photos"
