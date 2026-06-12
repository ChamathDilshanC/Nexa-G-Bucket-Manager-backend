"""Basic API smoke tests.

Author: Chamath Dilshan
"""

from fastapi.testclient import TestClient

from app.main import app


def test_root_renders_clickable_html_for_browser_requests() -> None:
    """Verify browser requests receive an HTML page with clickable endpoint links."""
    client = TestClient(app)
    response = client.get("/", headers={"accept": "text/html"})

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'href="http://testserver/health"' in response.text
    assert 'target="_blank"' in response.text
    assert "/health" in response.text
    assert "API Endpoints" in response.text


def test_root_returns_json_for_api_clients() -> None:
    """Verify API clients still receive JSON discovery metadata."""
    client = TestClient(app)
    response = client.get("/", headers={"accept": "application/json"})

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
