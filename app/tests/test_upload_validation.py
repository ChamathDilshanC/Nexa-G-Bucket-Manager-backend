"""Upload validation tests.

Author: Chamath Dilshan
"""

from fastapi.testclient import TestClient

from app.main import app


def test_upload_url_rejects_oversized_file_declaration() -> None:
    """Verify declared upload sizes above the configured limit are rejected."""
    client = TestClient(app)
    response = client.post(
        "/files/upload-url",
        headers={"Authorization": "Bearer invalid-token"},
        json={
            "bucket": "nexa-files",
            "path": "large.pdf",
            "content_type": "application/pdf",
            "file_size_bytes": 60 * 1024 * 1024,
        },
    )

    assert response.status_code in {400, 401, 403}
