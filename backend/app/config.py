"""Application configuration, loaded from environment / .env file."""
from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
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

    # AI explanation layer. Provider auto-selected by which key is present:
    # Gemini (if gemini_api_key) -> Anthropic (if anthropic_api_key) -> template.
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # Monte Carlo
    monte_carlo_runs: int = 20000

    # CORS
    cors_origins: str = "http://localhost:3000"

    @field_validator(
        "database_url",
        "data_provider",
        "football_data_api_key",
        "anthropic_api_key",
        "anthropic_model",
        "gemini_api_key",
        "gemini_model",
        "cors_origins",
        mode="after",
    )
    @classmethod
    def _strip(cls, v: str) -> str:
        # Env values (esp. secrets pasted into hosting dashboards) often pick up a
        # trailing newline/space, which is an illegal HTTP header value. Strip it.
        return v.strip() if isinstance(v, str) else v

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
