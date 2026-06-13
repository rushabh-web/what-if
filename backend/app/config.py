"""Application configuration, loaded from environment / .env file."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object. Values come from environment variables / .env."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database
    database_url: str = "sqlite:///./fifa.db"

    # Data provider: "seed" or "football-data"
    data_provider: str = "seed"
    football_data_api_key: str = ""

    # AI explanation layer
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"

    # Monte Carlo
    monte_carlo_runs: int = 20000

    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def normalized_database_url(self) -> str:
        """Rewrite a bare `postgresql://` URL (as Railway/Render provide) to use the
        psycopg3 driver SQLAlchemy expects."""
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        if url.startswith("postgres://"):  # some providers use this scheme
            return url.replace("postgres://", "postgresql+psycopg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor."""
    return Settings()
