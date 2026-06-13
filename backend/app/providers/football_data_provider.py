"""Football-Data.org provider (competition code "WC").

Note: World Cup 2026 fixtures may not be published on the free tier until closer
to the tournament. If the API returns no group-stage data, the factory falls
back to the seed provider so the app keeps working.
"""
from __future__ import annotations

from datetime import datetime

import httpx

from app.providers.base import DataProvider
from app.seed.data import TOURNAMENT_START
from app.seed.data import TEAMS as SEED_TEAMS

BASE_URL = "https://api.football-data.org/v4"
COMPETITION = "WC"

# Reuse seed ratings (by FIFA code) so the Poisson model has sensible strengths.
_SEED_RATING = {t["fifa_code"]: t["rating"] for t in SEED_TEAMS}


def _parse_date(raw: str | None) -> datetime:
    """Parse an ISO-8601 UTC string (e.g. '2026-06-11T19:00:00Z') to a naive datetime.

    SQLAlchemy/psycopg needs a real datetime for the Postgres timestamp column;
    a raw string only works on SQLite. Falls back to the tournament start date.
    """
    if not raw:
        return TOURNAMENT_START
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return TOURNAMENT_START


class FootballDataProvider(DataProvider):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._teams: list[dict] | None = None
        self._matches: list[dict] | None = None

    def _fetch_matches(self) -> list[dict]:
        headers = {"X-Auth-Token": self._api_key}
        url = f"{BASE_URL}/competitions/{COMPETITION}/matches"
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json().get("matches", [])

    @staticmethod
    def _group_letter(raw: str | None) -> str:
        if not raw:
            return ""
        return raw.replace("GROUP_", "").strip()[:1]

    def _load(self) -> None:
        raw_matches = self._fetch_matches()
        teams: dict[int, dict] = {}
        matches: list[dict] = []
        for m in raw_matches:
            if m.get("stage") != "GROUP_STAGE":
                continue
            group = self._group_letter(m.get("group"))
            for side in ("homeTeam", "awayTeam"):
                t = m.get(side) or {}
                tid = t.get("id")
                if tid and tid not in teams:
                    code = (t.get("tla") or "")[:3]
                    teams[tid] = {
                        "team_id": tid,
                        "name": t.get("name", "Unknown"),
                        "fifa_code": code,
                        "group_name": group,
                        "flag_url": t.get("crest", ""),
                        "rating": _SEED_RATING.get(code, 1700.0),
                    }
            score = (m.get("score") or {}).get("fullTime") or {}
            finished = m.get("status") == "FINISHED"
            matches.append(
                {
                    "match_id": m["id"],
                    "home_team_id": (m.get("homeTeam") or {}).get("id"),
                    "away_team_id": (m.get("awayTeam") or {}).get("id"),
                    "group_name": group,
                    "matchday": m.get("matchday") or 1,
                    "match_date": _parse_date(m.get("utcDate")),
                    "status": "finished" if finished else "scheduled",
                    "home_goals": score.get("home"),
                    "away_goals": score.get("away"),
                }
            )
        if not matches:
            raise RuntimeError("Football-Data returned no WC group-stage matches")
        self._teams = list(teams.values())
        self._matches = matches

    def get_teams(self) -> list[dict]:
        if self._teams is None:
            self._load()
        return [dict(t) for t in (self._teams or [])]

    def get_matches(self) -> list[dict]:
        if self._matches is None:
            self._load()
        return [dict(m) for m in (self._matches or [])]
