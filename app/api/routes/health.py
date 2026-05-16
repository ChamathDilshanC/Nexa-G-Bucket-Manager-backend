"""Health check endpoint.

Author: Chamath Dilshan
"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Simple probe endpoint to verify API availability."""
    return {"status": "ok"}
