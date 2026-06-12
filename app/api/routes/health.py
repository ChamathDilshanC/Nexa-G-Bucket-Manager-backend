"""Health and system info endpoints.

Author: Chamath Dilshan
"""

from fastapi import APIRouter, Request

from app.schemas.info import RootResponse, SystemInfoResponse
from app.services.api_discovery import build_root_response
from app.services.system_status import get_system_info

router = APIRouter(tags=["health"])


@router.get("/", response_model=RootResponse)
def root(request: Request) -> RootResponse:
    """Landing endpoint with full links, docs, and connectivity summary."""
    base_url = str(request.base_url).rstrip("/")
    return build_root_response(base_url)


@router.get("/health")
def health_check() -> dict[str, str]:
    """Simple probe endpoint to verify API availability."""
    return {"status": "ok"}


@router.get("/info", response_model=SystemInfoResponse)
def system_info() -> SystemInfoResponse:
    """Return Supabase, storage, and runtime configuration status."""
    return SystemInfoResponse(**get_system_info())
