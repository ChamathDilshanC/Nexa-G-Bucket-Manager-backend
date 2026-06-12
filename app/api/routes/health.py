"""Health and system info endpoints.

Author: Chamath Dilshan
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.schemas.info import RootResponse, SystemInfoResponse
from app.services.api_discovery import build_root_response
from app.services.root_html import build_root_html
from app.services.system_status import get_system_info

router = APIRouter(tags=["health"])


def _wants_html(request: Request) -> bool:
    """Return whether the client prefers an HTML landing page."""
    accept = request.headers.get("accept", "")
    if "application/json" in accept and "text/html" not in accept:
        return False
    return "text/html" in accept or "*/*" in accept


@router.get("/", response_model=None)
def root(request: Request) -> RootResponse | HTMLResponse:
    """Landing endpoint with clickable links for browsers and JSON for API clients."""
    base_url = str(request.base_url).rstrip("/")
    payload = build_root_response(base_url)

    if _wants_html(request):
        return HTMLResponse(content=build_root_html(payload))

    return JSONResponse(content=payload.model_dump())


@router.get("/health")
def health_check() -> dict[str, str]:
    """Simple probe endpoint to verify API availability."""
    return {"status": "ok"}


@router.get("/info", response_model=SystemInfoResponse)
def system_info() -> SystemInfoResponse:
    """Return Supabase, storage, and runtime configuration status."""
    return SystemInfoResponse(**get_system_info())
