"""Rule-based parser turning a question into scenario match results + a focus team.

Deterministic by design (the spec keeps the LLM out of calculations). Handles the
common MVP intents: a team winning / losing / drawing its next match, a team
winning all remaining matches, and a specific fixture between two named teams.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.schemas.match import ScenarioMatch


@dataclass
class ParsedQuery:
    focus_team_id: int | None = None
    scenario: list[ScenarioMatch] = field(default_factory=list)
    description: str = ""


_WIN_WORDS = ("win", "wins", "beat", "beats", "defeat", "defeats")
_LOSE_WORDS = ("lose", "loses", "lost", "loss")
_DRAW_WORDS = ("draw", "draws", "tie", "ties")
_ALL_WORDS = ("both", "all", "every", "remaining")


def _find_teams(text: str, teams: list[dict]) -> list[dict]:
    """Return teams mentioned in `text`, longest names first to avoid partials."""
    lowered = text.lower()
    found: list[tuple[int, dict]] = []
    for t in sorted(teams, key=lambda x: -len(x["name"])):
        name = t["name"].lower()
        code = t["fifa_code"].lower()
        pos = lowered.find(name)
        if pos == -1 and re.search(rf"\b{re.escape(code)}\b", lowered):
            pos = lowered.find(code)
        if pos != -1 and not any(t["team_id"] == f[1]["team_id"] for f in found):
            found.append((pos, t))
    found.sort(key=lambda x: x[0])  # by order of appearance
    return [t for _, t in found]


def _scheduled_for(team_id: int, matches: list[dict]) -> list[dict]:
    out = [
        m
        for m in matches
        if m["status"] != "finished"
        and team_id in (m["home_team_id"], m["away_team_id"])
    ]
    out.sort(key=lambda m: (m["matchday"], m["match_id"]))
    return out


def _result_for(team_id: int, match: dict, outcome: str) -> ScenarioMatch:
    """Build a ScenarioMatch where `team_id` gets the given outcome."""
    is_home = match["home_team_id"] == team_id
    if outcome == "win":
        winner_goals, loser_goals = 1, 0
        hg, ag = (winner_goals, loser_goals) if is_home else (loser_goals, winner_goals)
    elif outcome == "lose":
        hg, ag = (0, 1) if is_home else (1, 0)
    else:  # draw
        hg, ag = 1, 1
    return ScenarioMatch(match_id=match["match_id"], home_goals=hg, away_goals=ag)


def parse_query(query: str, teams: list[dict], matches: list[dict]) -> ParsedQuery:
    if not query or not query.strip():
        return ParsedQuery()

    text = query.strip()
    lowered = text.lower()
    mentioned = _find_teams(text, teams)
    if not mentioned:
        return ParsedQuery(description="No recognised team in the query.")

    primary = mentioned[0]
    focus_id = primary["team_id"]

    has_win = any(w in lowered for w in _WIN_WORDS)
    has_lose = any(w in lowered for w in _LOSE_WORDS)
    has_draw = any(w in lowered for w in _DRAW_WORDS)
    apply_all = any(w in lowered for w in _ALL_WORDS)

    # Two teams + a fixture between them → target that specific match.
    if len(mentioned) >= 2:
        other = mentioned[1]
        fixture = next(
            (
                m
                for m in matches
                if {m["home_team_id"], m["away_team_id"]}
                == {primary["team_id"], other["team_id"]}
                and m["status"] != "finished"
            ),
            None,
        )
        if fixture is not None:
            outcome = "win" if has_win else "lose" if has_lose else "draw"
            sm = _result_for(primary["team_id"], fixture, outcome)
            verb = {"win": "beats", "lose": "loses to", "draw": "draws with"}[outcome]
            return ParsedQuery(
                focus_team_id=focus_id,
                scenario=[sm],
                description=f"{primary['name']} {verb} {other['name']}",
            )

    upcoming = _scheduled_for(focus_id, matches)
    if not upcoming or not (has_win or has_lose or has_draw):
        # e.g. "Can Morocco still qualify?" — no result to apply, just focus.
        return ParsedQuery(
            focus_team_id=focus_id,
            scenario=[],
            description=f"Outlook for {primary['name']} (no result applied)",
        )

    outcome = "win" if has_win else "lose" if has_lose else "draw"
    targets = upcoming if apply_all else upcoming[:1]
    scenario = [_result_for(focus_id, m, outcome) for m in targets]
    verb = {"win": "wins", "lose": "loses", "draw": "draws"}[outcome]
    scope = " all remaining matches" if apply_all and len(targets) > 1 else " its next match"
    return ParsedQuery(
        focus_team_id=focus_id,
        scenario=scenario,
        description=f"{primary['name']} {verb}{scope}",
    )
