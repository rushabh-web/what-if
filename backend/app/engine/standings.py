"""Standings computation with FIFA group ranking tie-break rules.

Tie-break order (FIFA): 1) points, 2) goal difference, 3) goals scored,
4) head-to-head (points, then GD, then GF among the tied teams), 5) fair play,
6) drawing of lots. Fair-play data is not modelled here, so steps 5-6 are
replaced by a deterministic fallback (higher rating, then lower team_id) to keep
the engine reproducible.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import cmp_to_key

from app.schemas.standings import StandingRow


@dataclass
class _Stat:
    team_id: int
    name: str
    fifa_code: str
    group_name: str
    rating: float
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    gf: int = 0
    ga: int = 0

    @property
    def gd(self) -> int:
        return self.gf - self.ga

    @property
    def points(self) -> int:
        return self.wins * 3 + self.draws


def _finished(match: dict) -> bool:
    return (
        match.get("status") == "finished"
        and match.get("home_goals") is not None
        and match.get("away_goals") is not None
    )


def _accumulate(stat: _Stat, gf: int, ga: int) -> None:
    stat.played += 1
    stat.gf += gf
    stat.ga += ga
    if gf > ga:
        stat.wins += 1
    elif gf < ga:
        stat.losses += 1
    else:
        stat.draws += 1


def _head_to_head(tied: list[_Stat], matches: list[dict]) -> dict[int, tuple[int, int, int]]:
    """Mini-table (points, gd, gf) using only matches among the tied teams."""
    ids = {s.team_id for s in tied}
    mini: dict[int, _Stat] = {
        s.team_id: _Stat(s.team_id, s.name, s.fifa_code, s.group_name, s.rating) for s in tied
    }
    for m in matches:
        if not _finished(m):
            continue
        h, a = m["home_team_id"], m["away_team_id"]
        if h in ids and a in ids:
            _accumulate(mini[h], m["home_goals"], m["away_goals"])
            _accumulate(mini[a], m["away_goals"], m["home_goals"])
    return {tid: (s.points, s.gd, s.gf) for tid, s in mini.items()}


def compute_group_table(
    group_name: str, teams: list[dict], matches: list[dict]
) -> list[StandingRow]:
    """Compute the ordered standings table for one group."""
    members = [t for t in teams if t["group_name"] == group_name]
    stats: dict[int, _Stat] = {
        t["team_id"]: _Stat(
            team_id=t["team_id"],
            name=t["name"],
            fifa_code=t["fifa_code"],
            group_name=group_name,
            rating=float(t.get("rating", 1500.0)),
        )
        for t in members
    }
    group_matches = [m for m in matches if m["group_name"] == group_name]
    for m in group_matches:
        if not _finished(m):
            continue
        h, a = m["home_team_id"], m["away_team_id"]
        if h in stats and a in stats:
            _accumulate(stats[h], m["home_goals"], m["away_goals"])
            _accumulate(stats[a], m["away_goals"], m["home_goals"])

    ordered = _sort_stats(list(stats.values()), group_matches)
    rows: list[StandingRow] = []
    for i, s in enumerate(ordered):
        status = "qualified" if i < 2 else ("third" if i == 2 else "out")
        rows.append(
            StandingRow(
                position=i + 1,
                team_id=s.team_id,
                team=s.name,
                fifa_code=s.fifa_code,
                group_name=group_name,
                played=s.played,
                wins=s.wins,
                draws=s.draws,
                losses=s.losses,
                gf=s.gf,
                ga=s.ga,
                gd=s.gd,
                points=s.points,
                qualification_status=status,
            )
        )
    return rows


def _sort_stats(stats: list[_Stat], matches: list[dict]) -> list[_Stat]:
    """Order teams applying the full tie-break chain."""

    def base_key(s: _Stat) -> tuple[int, int, int]:
        return (s.points, s.gd, s.gf)

    # First pass: sort by the all-matches criteria.
    stats.sort(key=lambda s: (base_key(s), s.rating, -s.team_id), reverse=True)

    # Resolve clusters tied on (points, gd, gf) using head-to-head.
    result: list[_Stat] = []
    i = 0
    while i < len(stats):
        j = i
        while j + 1 < len(stats) and base_key(stats[j + 1]) == base_key(stats[i]):
            j += 1
        cluster = stats[i : j + 1]
        if len(cluster) > 1:
            h2h = _head_to_head(cluster, matches)

            def cmp(a: _Stat, b: _Stat) -> int:
                ka, kb = h2h[a.team_id], h2h[b.team_id]
                if ka != kb:
                    return -1 if ka > kb else 1
                # Deterministic fallback (stand-in for fair play / draw of lots).
                if a.rating != b.rating:
                    return -1 if a.rating > b.rating else 1
                return -1 if a.team_id < b.team_id else 1

            cluster.sort(key=cmp_to_key(cmp))
        result.extend(cluster)
        i = j + 1
    return result


def compute_all_tables(
    teams: list[dict], matches: list[dict]
) -> dict[str, list[StandingRow]]:
    groups = sorted({t["group_name"] for t in teams})
    return {g: compute_group_table(g, teams, matches) for g in groups}
