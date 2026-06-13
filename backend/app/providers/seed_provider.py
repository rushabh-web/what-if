"""Offline seed provider — works with zero external dependencies."""
from __future__ import annotations

from app.providers.base import DataProvider
from app.seed.data import build_matches, build_teams


class SeedProvider(DataProvider):
    def __init__(self) -> None:
        self._teams = build_teams()
        self._matches = build_matches(self._teams)

    def get_teams(self) -> list[dict]:
        return [dict(t) for t in self._teams]

    def get_matches(self) -> list[dict]:
        return [dict(m) for m in self._matches]
