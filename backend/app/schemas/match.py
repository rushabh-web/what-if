"""Match schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    match_id: int
    home_team_id: int
    away_team_id: int
    home_team: str = ""
    away_team: str = ""
    home_code: str = ""
    away_code: str = ""
    group_name: str
    matchday: int
    match_date: datetime
    status: str
    home_goals: int | None = None
    away_goals: int | None = None


class ScenarioMatch(BaseModel):
    """A hypothetical match result supplied by the user."""

    match_id: int
    home_goals: int = Field(ge=0, le=99)
    away_goals: int = Field(ge=0, le=99)
