"""Probability schemas."""
from __future__ import annotations

from pydantic import BaseModel


class TeamProbabilities(BaseModel):
    """Monte Carlo output for a single team (values are 0..1 probabilities)."""

    team_id: int
    team: str
    fifa_code: str
    group_name: str
    qualification_probability: float
    group_win_probability: float
    round_of_16_probability: float
    quarter_final_probability: float
    semi_final_probability: float
    final_probability: float
    championship_probability: float
