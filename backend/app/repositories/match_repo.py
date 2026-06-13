"""Match repository."""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.match import Match


class MatchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def all(self) -> list[Match]:
        return list(self.db.scalars(select(Match).order_by(Match.match_date, Match.match_id)))

    def get(self, match_id: int) -> Match | None:
        return self.db.get(Match, match_id)

    def by_group(self, group_name: str) -> list[Match]:
        return list(
            self.db.scalars(
                select(Match).where(Match.group_name == group_name).order_by(Match.matchday)
            )
        )

    def for_team(self, team_id: int) -> list[Match]:
        return list(
            self.db.scalars(
                select(Match)
                .where((Match.home_team_id == team_id) | (Match.away_team_id == team_id))
                .order_by(Match.match_date)
            )
        )

    def count(self) -> int:
        return int(self.db.scalar(select(func.count()).select_from(Match)) or 0)

    def bulk_insert(self, rows: list[dict]) -> None:
        self.db.add_all([Match(**r) for r in rows])
        self.db.commit()
