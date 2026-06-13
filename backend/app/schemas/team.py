"""Team schemas."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: int
    name: str
    fifa_code: str
    group_name: str
    flag_url: str = ""
    rating: float = 1500.0
