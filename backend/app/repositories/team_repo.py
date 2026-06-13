"""Team repository."""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.team import Team


class TeamRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def all(self) -> list[Team]:
        return list(self.db.scalars(select(Team).order_by(Team.group_name, Team.team_id)))

    def get(self, team_id: int) -> Team | None:
        return self.db.get(Team, team_id)

    def by_group(self, group_name: str) -> list[Team]:
        return list(
            self.db.scalars(select(Team).where(Team.group_name == group_name).order_by(Team.team_id))
        )

    def by_code(self, fifa_code: str) -> Team | None:
        return self.db.scalars(select(Team).where(Team.fifa_code == fifa_code.upper())).first()

    def count(self) -> int:
        return int(self.db.scalar(select(func.count()).select_from(Team)) or 0)

    def bulk_insert(self, rows: list[dict]) -> None:
        self.db.add_all([Team(**r) for r in rows])
        self.db.commit()
