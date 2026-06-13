"""Simulation request/response schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.knockout import KnockoutPath
from app.schemas.match import ScenarioMatch
from app.schemas.probability import TeamProbabilities
from app.schemas.standings import StandingRow


class GroupTable(BaseModel):
    group_name: str
    rows: list[StandingRow]


class SimulateRequest(BaseModel):
    """Either an explicit scenario, a natural-language query, or both.

    If `query` is provided, the NLP parser converts it into scenario matches.
    Explicit `scenario` entries take precedence and are merged with parsed ones.
    """

    scenario: list[ScenarioMatch] = Field(default_factory=list)
    query: str | None = None
    # Optional: focus the response (probabilities/knockout) on one team.
    focus_team_id: int | None = None


class SimulateResponse(BaseModel):
    parsed_query: str | None = None
    applied_scenario: list[ScenarioMatch] = []
    updated_standings: list[GroupTable] = []
    qualification_probabilities: list[TeamProbabilities] = []
    knockout_path: KnockoutPath | None = None
    ai_summary: str = ""


class ShareCardRequest(BaseModel):
    title: str = "WHAT IF"
    scenario_text: str
    team: str
    before_probability: float  # 0..1
    after_probability: float  # 0..1
    most_likely_opponent: str = ""
