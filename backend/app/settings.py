from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    dashboard_db_path: Path = Field(default=Path("data/dashboard.db"), alias="DASHBOARD_DB_PATH")
    dashboard_sanitized_dir: Path = Field(
        default=Path("data/sanitized"), alias="DASHBOARD_SANITIZED_DIR"
    )
    dashboard_api_host: str = Field(default="127.0.0.1", alias="DASHBOARD_API_HOST")
    dashboard_api_port: int = Field(default=8000, alias="DASHBOARD_API_PORT")
    dashboard_cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="DASHBOARD_CORS_ORIGINS",
    )
    codex_home: Path | None = Field(default=None, alias="CODEX_HOME")
    woodcraft_brief_source: Path | None = Field(default=None, alias="WOODCRAFT_BRIEF_SOURCE")

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.dashboard_cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
