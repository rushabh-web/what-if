"""DataProvider interface.

Implementations supply raw teams and matches. Standings and group tables are
derived from those via the (pure, deterministic) standings engine, so every
provider gets consistent table logic for free.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.engine.standings import compute_all_tables, compute_group_table
from app.schemas.standings import StandingRow


class DataProvider(ABC):
    @abstractmethod
    def get_teams(self) -> list[dict]:
        """Return team rows: team_id, name, fifa_code, group_name, flag_url, rating."""

    @abstractmethod
    def get_matches(self) -> list[dict]:
        """Return match rows: match_id, home_team_id, away_team_id, group_name,
        matchday, match_date, status, home_goals, away_goals."""

    def get_standings(self) -> dict[str, list[StandingRow]]:
        """Computed standings for every group."""
        return compute_all_tables(self.get_teams(), self.get_matches())

    def get_group_table(self, group_name: str) -> list[StandingRow]:
        """Computed standings for a single group."""
        return compute_group_table(group_name, self.get_teams(), self.get_matches())
