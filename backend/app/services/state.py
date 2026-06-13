"""Load current tournament state from the DB as plain dicts for the engines."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.match import Match
from app.models.team import Team
from app.repositories import MatchRepository, TeamRepository
from app.schemas.match import MatchOut


def team_to_dict(t: Team) -> dict:
    return {
        "team_id": t.team_id,
        "name": t.name,
        "fifa_code": t.fifa_code,
        "group_name": t.group_name,
        "flag_url": t.flag_url,
        "rating": t.rating,
    }


def match_to_dict(m: Match) -> dict:
    return {
        "match_id": m.match_id,
        "home_team_id": m.home_team_id,
        "away_team_id": m.away_team_id,
        "group_name": m.group_name,
        "matchday": m.matchday,
        "match_date": m.match_date,
        "status": m.status,
        "home_goals": m.home_goals,
        "away_goals": m.away_goals,
    }


def load_state(db: Session) -> tuple[list[dict], list[dict]]:
    """Return (teams, matches) as dicts ready for the engines."""
    teams = [team_to_dict(t) for t in TeamRepository(db).all()]
    matches = [match_to_dict(m) for m in MatchRepository(db).all()]
    return teams, matches


def enrich_match(m: dict, teams_by_id: dict[int, dict]) -> MatchOut:
    """Attach team names/codes to a match dict for API output."""
    home = teams_by_id.get(m["home_team_id"], {})
    away = teams_by_id.get(m["away_team_id"], {})
    return MatchOut(
        **m,
        home_team=home.get("name", ""),
        away_team=away.get("name", ""),
        home_code=home.get("fifa_code", ""),
        away_code=away.get("fifa_code", ""),
    )
