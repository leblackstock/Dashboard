from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.ai_codex import router as ai_codex_router
from backend.app.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Dashboard API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    app.include_router(ai_codex_router)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "dashboard-api"}

    return app


app = create_app()
