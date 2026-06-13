"""Standings schemas."""
from __future__ import annotations

from pydantic import BaseModel


class StandingRow(BaseModel):
    """A single team's row in a computed group table."""

    position: int
    team_id: int
    team: str
    fifa_code: str
    group_name: str
    played: int
    wins: int
    draws: int
    losses: int
    gf: int
    ga: int
    gd: int
    points: int
    # "qualified" (top 2), "third" (in 3rd, may advance as best-third), or "out".
    qualification_status: str = "out"
