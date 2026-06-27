from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.ai_codex import router as ai_codex_router
from backend.app.routes.blocked_items import router as blocked_items_router
from backend.app.routes.brief_suggestions import router as brief_suggestions_router
from backend.app.routes.collector_health import router as collector_health_router
from backend.app.routes.daily import router as daily_router
from backend.app.routes.projects import router as projects_router
from backend.app.routes.quick_captures import router as quick_captures_router
from backend.app.routes.top_items import router as top_items_router
from backend.app.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Dashboard API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["*"],
    )
    app.include_router(ai_codex_router)
    app.include_router(daily_router)
    app.include_router(projects_router)
    app.include_router(top_items_router)
    app.include_router(brief_suggestions_router)
    app.include_router(blocked_items_router)
    app.include_router(quick_captures_router)
    app.include_router(collector_health_router)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "dashboard-api"}

    return app


app = create_app()
