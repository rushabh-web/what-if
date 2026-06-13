"""Match ORM model."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    match_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), index=True)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"), index=True)
    group_name: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    matchday: Mapped[int] = mapped_column(Integer, default=1)
    match_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # "scheduled" or "finished"
    status: Mapped[str] = mapped_column(String(12), default="scheduled", index=True)
    home_goals: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_goals: Mapped[int | None] = mapped_column(Integer, nullable=True)
