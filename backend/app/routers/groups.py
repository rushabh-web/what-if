"""Group endpoints (Group Explorer)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.engine.standings import compute_group_table
from app.schemas.standings import StandingRow
from app.schemas.team import TeamOut
from app.services.state import load_state

router = APIRouter(prefix="/groups", tags=["groups"])


class GroupDetail(BaseModel):
    group_name: str
    teams: list[TeamOut]
    table: list[StandingRow]


@router.get("", response_model=list[GroupDetail])
def list_groups(db: Session = Depends(get_db)) -> list[GroupDetail]:
    teams, matches = load_state(db)
    groups = sorted({t["group_name"] for t in teams})
    details: list[GroupDetail] = []
    for g in groups:
        members = [TeamOut(**t) for t in teams if t["group_name"] == g]
        details.append(
            GroupDetail(
                group_name=g,
                teams=members,
                table=compute_group_table(g, teams, matches),
            )
        )
    return details
