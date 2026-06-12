"""System info endpoint tests.

Author: Chamath Dilshan
"""

from fastapi.testclient import TestClient

from app.main import app


def test_info_endpoint_returns_expected_sections() -> None:
    """Verify the info endpoint exposes all status sections."""
    client = TestClient(app)
    response = client.get("/info")

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] in {"ok", "degraded", "error"}
    assert "app" in payload
    assert "supabase" in payload
    assert "storage" in payload
    assert "settings" in payload

    assert payload["app"]["name"]
    assert "configured" in payload["supabase"]
    assert "connected" in payload["supabase"]
    assert "jwt_secret_configured" in payload["supabase"]
    assert "service_role_key_configured" in payload["supabase"]
    assert "default_bucket_configured" in payload["storage"]
    assert "buckets" in payload["storage"]
    assert isinstance(payload["storage"]["buckets"], list)
