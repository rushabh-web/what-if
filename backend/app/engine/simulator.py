"""Deterministic scenario simulator.

Overlays hypothetical match results onto the current match set so the standings,
probability and knockout engines can recompute from a single mutated state.
No randomness, no LLM — given the same inputs it always returns the same output.
"""
from __future__ import annotations

from app.schemas.match import ScenarioMatch


def apply_scenario(matches: list[dict], scenario: list[ScenarioMatch]) -> list[dict]:
    """Return a new match list with each scenario result applied (marked finished)."""
    override = {s.match_id: s for s in scenario}
    result: list[dict] = []
    for m in matches:
        m = dict(m)
        if m["match_id"] in override:
            s = override[m["match_id"]]
            m["home_goals"] = s.home_goals
            m["away_goals"] = s.away_goals
            m["status"] = "finished"
        result.append(m)
    return result


def unknown_match_ids(matches: list[dict], scenario: list[ScenarioMatch]) -> list[int]:
    """Scenario match_ids that don't exist in the current match set (for validation)."""
    known = {m["match_id"] for m in matches}
    return [s.match_id for s in scenario if s.match_id not in known]
