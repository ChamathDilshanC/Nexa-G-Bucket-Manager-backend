"""Basic API smoke tests.

Author: Chamath Dilshan
"""

from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_ok() -> None:
    """Verify the health endpoint is always available."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
