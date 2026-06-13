"""Provider selection with graceful fallback to the offline seed dataset."""
from __future__ import annotations

import logging

from app.config import get_settings
from app.providers.base import DataProvider
from app.providers.seed_provider import SeedProvider

logger = logging.getLogger(__name__)


def get_provider() -> DataProvider:
    settings = get_settings()
    if settings.data_provider == "football-data" and settings.football_data_api_key:
        try:
            from app.providers.football_data_provider import FootballDataProvider

            provider = FootballDataProvider(settings.football_data_api_key)
            provider.get_matches()  # probe; raises if WC data is unavailable
            logger.info("Using Football-Data provider")
            return provider
        except Exception as exc:  # noqa: BLE001 - fall back rather than crash
            logger.warning("Football-Data unavailable (%s); falling back to seed data", exc)
    return SeedProvider()
