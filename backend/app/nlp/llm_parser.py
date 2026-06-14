"""LLM-backed query parser (Gemini).

Translates a free-form question into structured simulation inputs — match
results to apply and the team to report on. This is *intent parsing only*; the
deterministic engines still compute every standing and probability. The LLM is
never given or asked for any numeric outcome.

Falls back to the rule-based parser when no Gemini key is set or on any error.
"""
from __future__ import annotations

import json
import logging

import httpx

from app.nlp.parser import ParsedQuery
from app.schemas.match import ScenarioMatch

logger = logging.getLogger(__name__)

_SYSTEM = (
    "You convert a football World Cup what-if question into structured JSON. "
    "You are given the list of teams and the remaining (unplayed) fixtures with "
    "their match_id and which side is home/away. Rules:\n"
    "- 'scenario' = the match results the user wants applied. Use ONLY match_ids "
    "from the provided fixtures. home_goals/away_goals follow the home/away sides "
    "shown for that match. If the user gives a scoreline (e.g. 'wins 3-0'), use it; "
    "otherwise pick a result consistent with the verb (win=1-0 for that team, "
    "draw=1-1, lose=0-1 for that team).\n"
    "- 'today'/'its next match' for a team = that team's earliest listed fixture.\n"
    "- 'focus_team_id' = the team the user wants the outlook/chances for. If the "
    "question asks about a different team than the one whose result changes (e.g. "
    "'if Curacao wins, what are Germany's chances'), focus on the asked-about team.\n"
    "- If no concrete result can be applied, return an empty scenario but still set "
    "focus_team_id to the most relevant team.\n"
    "- Never invent match_ids or team_ids. Output JSON only."
)

_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "focus_team_id": {"type": "integer", "nullable": True},
        "scenario": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "match_id": {"type": "integer"},
                    "home_goals": {"type": "integer"},
                    "away_goals": {"type": "integer"},
                },
                "required": ["match_id", "home_goals", "away_goals"],
            },
        },
        "description": {"type": "string"},
    },
    "required": ["focus_team_id", "scenario", "description"],
}


def _context(teams: list[dict], matches: list[dict]) -> str:
    name = {t["team_id"]: t for t in teams}
    team_lines = [
        f"- {t['name']} (id {t['team_id']}, group {t['group_name']})"
        for t in sorted(teams, key=lambda t: t["name"])
    ]
    fixture_lines = []
    for m in matches:
        if m["status"] == "finished":
            continue
        h = name.get(m["home_team_id"], {})
        a = name.get(m["away_team_id"], {})
        fixture_lines.append(
            f"- match_id {m['match_id']} (matchday {m['matchday']}): "
            f"HOME {h.get('name', '?')} (id {m['home_team_id']}) vs "
            f"AWAY {a.get('name', '?')} (id {m['away_team_id']})"
        )
    return "TEAMS:\n" + "\n".join(team_lines) + "\n\nREMAINING FIXTURES:\n" + "\n".join(fixture_lines)


def parse_query_llm(
    query: str, teams: list[dict], matches: list[dict], api_key: str, model: str
) -> ParsedQuery:
    prompt = (
        f"{_context(teams, matches)}\n\nQUESTION: {query!r}\n\n"
        "Return the JSON described by the schema."
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": _SYSTEM}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": _RESPONSE_SCHEMA,
            "temperature": 0.1,
            "maxOutputTokens": 800,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    with httpx.Client(timeout=20.0) as client:
        resp = client.post(
            url,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"Gemini returned no candidates: {data}")
    text = "".join(
        p.get("text", "") for p in candidates[0].get("content", {}).get("parts", [])
    ).strip()
    parsed = json.loads(text)

    return _validate(parsed, teams, matches, query)


def _validate(parsed: dict, teams: list[dict], matches: list[dict], query: str) -> ParsedQuery:
    """Reject anything that doesn't reference real matches/teams; clamp goals."""
    valid_match = {m["match_id"]: m for m in matches if m["status"] != "finished"}
    valid_team = {t["team_id"] for t in teams}

    scenario: list[ScenarioMatch] = []
    for s in parsed.get("scenario", []) or []:
        mid = s.get("match_id")
        if mid in valid_match:
            scenario.append(
                ScenarioMatch(
                    match_id=mid,
                    home_goals=max(0, min(99, int(s.get("home_goals", 0)))),
                    away_goals=max(0, min(99, int(s.get("away_goals", 0)))),
                )
            )

    focus = parsed.get("focus_team_id")
    if focus not in valid_team:
        focus = None

    description = (parsed.get("description") or "").strip() or query
    return ParsedQuery(focus_team_id=focus, scenario=scenario, description=description)
