from __future__ import annotations

from fastapi import FastAPI

from app.logging_config import configure_logging
from app.api.routes_health import router as health_router
from app.api.routes_search import router as search_router
from app.api.routes_brief import router as brief_router


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="ppp-ai-search-copilot", version="0.1.0")
    app.include_router(health_router)
    app.include_router(search_router, prefix="/search", tags=["search"])
    app.include_router(brief_router, prefix="/brief", tags=["brief"])
    return app


app = create_app()

