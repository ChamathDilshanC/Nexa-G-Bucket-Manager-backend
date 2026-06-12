"""Basic API smoke tests.

Author: Chamath Dilshan
"""

from fastapi.testclient import TestClient

from app.main import app


def test_root_pretty_prints_json_for_browser_requests() -> None:
    """Verify browser requests receive indented JSON in development."""
    client = TestClient(app)
    response = client.get("/", headers={"accept": "text/html"})

    assert response.status_code == 200
    assert "\n" in response.text
    assert '  "name"' in response.text


def test_root_returns_api_links() -> None:
    """Verify the root endpoint exposes rich discovery metadata."""
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "running"
    assert payload["version"]
    assert payload["base_url"].startswith("http://")
    assert payload["docs"]["swagger"]["url"].endswith("/docs")
    assert payload["docs"]["redoc"]["url"].endswith("/redoc")
    assert payload["docs"]["openapi"]["url"].endswith("/openapi.json")
    assert payload["detailed_status_url"].endswith("/info")
    assert payload["connectivity"]["overall_status"] in {"ok", "degraded", "error"}
    assert len(payload["links"]) >= 8
    assert any(link["path"] == "/health" for link in payload["links"])


def test_health_check_returns_ok() -> None:
    """Verify the health endpoint is always available."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
