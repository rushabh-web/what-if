"""Simulation history ORM model."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Simulation(Base):
    __tablename__ = "simulations"

    simulation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_input: Mapped[str] = mapped_column(Text, default="")
    # JSON-encoded result payload.
    simulation_result: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
