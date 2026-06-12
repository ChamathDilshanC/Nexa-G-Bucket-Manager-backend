"""Pretty JSON middleware for browser-friendly API responses.

Author: Chamath Dilshan
"""

import json
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.config import get_settings


class PrettyJSONMiddleware(BaseHTTPMiddleware):
    """Indent JSON responses when a browser requests the API in development."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Pretty-print JSON responses for browser visits during local development."""
        response = await call_next(request)
        settings = get_settings()

        if settings.app_env != "development":
            return response

        accept = request.headers.get("accept", "")
        if "text/html" not in accept:
            return response

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        body = b"".join([chunk async for chunk in response.body_iterator])
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        pretty = json.dumps(parsed, indent=2, ensure_ascii=False).encode("utf-8")
        headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() not in {"content-length", "transfer-encoding"}
        }
        headers["content-length"] = str(len(pretty))

        return Response(
            content=pretty,
            status_code=response.status_code,
            headers=headers,
            media_type="application/json",
        )
