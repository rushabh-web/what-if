"""Offline seed dataset for the FIFA World Cup 2026 (48 teams, 12 groups).

The real final draw post-dates this build, so this is a *plausible* configuration
used so the app runs fully offline. Swap in real data via the Football-Data
provider without touching any other code.

Match state: Matchday 1 is played (deterministic scorelines derived from team
ratings) and Matchdays 2 & 3 are unplayed — a realistic mid-group-stage state
that makes "what-if" scenarios and probabilities meaningful.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

# (name, fifa_code, group, rating) — rating is an Elo-like strength for the Poisson model.
TEAMS: list[dict] = [
    # Group A
    {"name": "Mexico", "fifa_code": "MEX", "group_name": "A", "rating": 1840},
    {"name": "Croatia", "fifa_code": "CRO", "group_name": "A", "rating": 1900},
    {"name": "Saudi Arabia", "fifa_code": "KSA", "group_name": "A", "rating": 1610},
    {"name": "South Africa", "fifa_code": "RSA", "group_name": "A", "rating": 1560},
    # Group B
    {"name": "Canada", "fifa_code": "CAN", "group_name": "B", "rating": 1730},
    {"name": "Belgium", "fifa_code": "BEL", "group_name": "B", "rating": 1970},
    {"name": "Ecuador", "fifa_code": "ECU", "group_name": "B", "rating": 1760},
    {"name": "Qatar", "fifa_code": "QAT", "group_name": "B", "rating": 1540},
    # Group C
    {"name": "United States", "fifa_code": "USA", "group_name": "C", "rating": 1800},
    {"name": "Netherlands", "fifa_code": "NED", "group_name": "C", "rating": 1990},
    {"name": "Egypt", "fifa_code": "EGY", "group_name": "C", "rating": 1690},
    {"name": "Uzbekistan", "fifa_code": "UZB", "group_name": "C", "rating": 1570},
    # Group D
    {"name": "Argentina", "fifa_code": "ARG", "group_name": "D", "rating": 2090},
    {"name": "Norway", "fifa_code": "NOR", "group_name": "D", "rating": 1850},
    {"name": "Nigeria", "fifa_code": "NGA", "group_name": "D", "rating": 1720},
    {"name": "Panama", "fifa_code": "PAN", "group_name": "D", "rating": 1560},
    # Group E
    {"name": "France", "fifa_code": "FRA", "group_name": "E", "rating": 2060},
    {"name": "Senegal", "fifa_code": "SEN", "group_name": "E", "rating": 1810},
    {"name": "Japan", "fifa_code": "JPN", "group_name": "E", "rating": 1820},
    {"name": "New Zealand", "fifa_code": "NZL", "group_name": "E", "rating": 1500},
    # Group F
    {"name": "Brazil", "fifa_code": "BRA", "group_name": "F", "rating": 2050},
    {"name": "Switzerland", "fifa_code": "SUI", "group_name": "F", "rating": 1830},
    {"name": "South Korea", "fifa_code": "KOR", "group_name": "F", "rating": 1780},
    {"name": "Honduras", "fifa_code": "HON", "group_name": "F", "rating": 1540},
    # Group G
    {"name": "England", "fifa_code": "ENG", "group_name": "G", "rating": 2030},
    {"name": "Uruguay", "fifa_code": "URU", "group_name": "G", "rating": 1880},
    {"name": "Ivory Coast", "fifa_code": "CIV", "group_name": "G", "rating": 1700},
    {"name": "Jordan", "fifa_code": "JOR", "group_name": "G", "rating": 1530},
    # Group H
    {"name": "Spain", "fifa_code": "ESP", "group_name": "H", "rating": 2080},
    {"name": "Colombia", "fifa_code": "COL", "group_name": "H", "rating": 1870},
    {"name": "Australia", "fifa_code": "AUS", "group_name": "H", "rating": 1700},
    {"name": "Cape Verde", "fifa_code": "CPV", "group_name": "H", "rating": 1560},
    # Group I
    {"name": "Portugal", "fifa_code": "POR", "group_name": "I", "rating": 2010},
    {"name": "Denmark", "fifa_code": "DEN", "group_name": "I", "rating": 1840},
    {"name": "Cameroon", "fifa_code": "CMR", "group_name": "I", "rating": 1690},
    {"name": "Curacao", "fifa_code": "CUW", "group_name": "I", "rating": 1510},
    # Group J
    {"name": "Germany", "fifa_code": "GER", "group_name": "J", "rating": 1980},
    {"name": "Morocco", "fifa_code": "MAR", "group_name": "J", "rating": 1860},
    {"name": "Iran", "fifa_code": "IRN", "group_name": "J", "rating": 1680},
    {"name": "Costa Rica", "fifa_code": "CRC", "group_name": "J", "rating": 1560},
    # Group K
    {"name": "Italy", "fifa_code": "ITA", "group_name": "K", "rating": 1960},
    {"name": "Serbia", "fifa_code": "SRB", "group_name": "K", "rating": 1770},
    {"name": "Ghana", "fifa_code": "GHA", "group_name": "K", "rating": 1690},
    {"name": "Jamaica", "fifa_code": "JAM", "group_name": "K", "rating": 1540},
    # Group L
    {"name": "Portugal B", "fifa_code": "POL", "group_name": "L", "rating": 1800},
    {"name": "Tunisia", "fifa_code": "TUN", "group_name": "L", "rating": 1670},
    {"name": "Paraguay", "fifa_code": "PAR", "group_name": "L", "rating": 1700},
    {"name": "Peru", "fifa_code": "PER", "group_name": "L", "rating": 1650},
]

# Fix the Group L placeholder name/code to a real distinct team (Poland).
TEAMS[44] = {"name": "Poland", "fifa_code": "POL", "group_name": "L", "rating": 1800}

GROUPS = [chr(ord("A") + i) for i in range(12)]
TOURNAMENT_START = datetime(2026, 6, 11, 18, 0, 0)

# Round-robin pairings (indices within a group's 4-team list), by matchday.
_ROUND_ROBIN = {
    1: [(0, 1), (2, 3)],
    2: [(0, 2), (1, 3)],
    3: [(0, 3), (1, 2)],
}


def _expected_goals(att_rating: float, def_rating: float, home_adv: float = 0.0) -> float:
    """League-average ~1.35 goals, scaled by the rating gap (logistic-ish)."""
    base = 1.35
    diff = (att_rating - def_rating + home_adv) / 600.0
    return max(0.15, base * (10 ** diff))


def build_teams() -> list[dict]:
    """Return team rows with stable 1-based team_ids assigned in declared order."""
    return [{"team_id": i + 1, "flag_url": "", **t} for i, t in enumerate(TEAMS)]


def build_matches(teams: list[dict]) -> list[dict]:
    """Generate all 72 group-stage fixtures; Matchday 1 is played deterministically."""
    by_group: dict[str, list[dict]] = {g: [] for g in GROUPS}
    for t in teams:
        by_group[t["group_name"]].append(t)
    for g in by_group:
        by_group[g].sort(key=lambda t: t["team_id"])

    rng = random.Random(2026)  # deterministic scorelines
    matches: list[dict] = []
    match_id = 1
    for g in GROUPS:
        members = by_group[g]
        for md in (1, 2, 3):
            for hi, ai in _ROUND_ROBIN[md]:
                home, away = members[hi], members[ai]
                date = TOURNAMENT_START + timedelta(days=(md - 1) * 5 + (hi % 2), hours=(match_id % 4) * 2)
                played = md == 1
                hg = ag = None
                if played:
                    hx = _expected_goals(home["rating"], away["rating"], home_adv=40)
                    ax = _expected_goals(away["rating"], home["rating"])
                    hg = _poisson(rng, hx)
                    ag = _poisson(rng, ax)
                matches.append(
                    {
                        "match_id": match_id,
                        "home_team_id": home["team_id"],
                        "away_team_id": away["team_id"],
                        "group_name": g,
                        "matchday": md,
                        "match_date": date,
                        "status": "finished" if played else "scheduled",
                        "home_goals": hg,
                        "away_goals": ag,
                    }
                )
                match_id += 1
    return matches


def _poisson(rng: random.Random, lam: float) -> int:
    """Knuth's Poisson sampler (so seed data needs no numpy dependency)."""
    import math

    el = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= el:
            return k - 1
