"""Team endpoints, including the Team Explorer outlook."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.engine.knockout import project_path
from app.repositories import MatchRepository, TeamRepository
from app.schemas.match import MatchOut
from app.schemas.knockout import KnockoutPath
from app.schemas.probability import TeamProbabilities
from app.schemas.team import TeamOut
from app.services.probabilities import probabilities_for
from app.services.state import enrich_match, load_state, match_to_dict

router = APIRouter(prefix="/teams", tags=["teams"])


class TeamOutlook(BaseModel):
    team: TeamOut
    probabilities: TeamProbabilities | None
    remaining_matches: list[MatchOut]
    knockout_path: KnockoutPath | None


@router.get("", response_model=list[TeamOut])
def list_teams(db: Session = Depends(get_db)) -> list[TeamOut]:
    return [TeamOut.model_validate(t) for t in TeamRepository(db).all()]


@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)) -> TeamOut:
    team = TeamRepository(db).get(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamOut.model_validate(team)


@router.get("/{team_id}/outlook", response_model=TeamOutlook)
def team_outlook(team_id: int, db: Session = Depends(get_db)) -> TeamOutlook:
    team = TeamRepository(db).get(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    teams, matches = load_state(db)
    name_by_id = {t["team_id"]: t for t in teams}
    runs = get_settings().monte_carlo_runs
    probs = probabilities_for(teams, matches, runs)
    team_probs = next((p for p in probs if p.team_id == team_id), None)

    remaining = [
        enrich_match(match_to_dict(m), name_by_id)
        for m in MatchRepository(db).for_team(team_id)
        if m.status != "finished"
    ]
    path = project_path(teams, matches, team_id)

    return TeamOutlook(
        team=TeamOut.model_validate(team),
        probabilities=team_probs,
        remaining_matches=remaining,
        knockout_path=path,
    )
