"""FastAPI application entrypoint.

Author: Chamath Dilshan
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.buckets import router as buckets_router
from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router
from app.api.routes.shares import router as shares_router
from app.api.routes.signed_urls import router as signed_urls_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.pretty_json import PrettyJSONMiddleware

settings = get_settings()
configure_logging()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(PrettyJSONMiddleware)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(buckets_router)
app.include_router(files_router)
app.include_router(signed_urls_router)
app.include_router(shares_router)
