"""Match endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.match import MatchOut
from app.services.state import enrich_match, load_state

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[MatchOut])
def list_matches(
    group: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[MatchOut]:
    teams, matches = load_state(db)
    teams_by_id = {t["team_id"]: t for t in teams}
    if group:
        matches = [m for m in matches if m["group_name"] == group.upper()]
    if status:
        matches = [m for m in matches if m["status"] == status]
    return [enrich_match(m, teams_by_id) for m in matches]
