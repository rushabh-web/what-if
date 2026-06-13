"""Knockout path schemas."""
from __future__ import annotations

from pydantic import BaseModel


class KnockoutRound(BaseModel):
    """One projected stage on a team's path through the bracket."""

    round_name: str  # "Round of 32", "Round of 16", ...
    opponent_team_id: int | None = None
    opponent: str = "TBD"
    opponent_code: str = ""
    win_probability: float = 0.0  # probability of winning THIS tie


class KnockoutPath(BaseModel):
    team_id: int
    team: str
    seeded_position: str = ""  # e.g. "1A" (winner of group A)
    rounds: list[KnockoutRound] = []
