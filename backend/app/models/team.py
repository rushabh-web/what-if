"""Team ORM model."""
from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    team_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    fifa_code: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    group_name: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    flag_url: Mapped[str] = mapped_column(String(255), default="")
    # Strength rating used by the Poisson match model (offline approximation of Elo).
    rating: Mapped[float] = mapped_column(Float, default=1500.0)
