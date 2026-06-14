"""Orchestrates the /simulate flow: parse -> apply -> recompute -> explain."""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.ai import ExplanationContext, generate_explanation
from app.config import get_settings
from app.engine.knockout import project_path
from app.engine.simulator import apply_scenario, unknown_match_ids
from app.engine.standings import compute_all_tables
from app.nlp import smart_parse
from app.repositories import SimulationRepository
from app.schemas.match import ScenarioMatch
from app.schemas.probability import TeamProbabilities
from app.schemas.simulation import (
    GroupTable,
    SimulateRequest,
    SimulateResponse,
)
from app.services.probabilities import probabilities_for
from app.services.state import load_state


class SimulationError(ValueError):
    """Raised for invalid simulation input (e.g. unknown match id)."""


def _tables_to_groups(tables: dict) -> list[GroupTable]:
    return [GroupTable(group_name=g, rows=rows) for g, rows in sorted(tables.items())]


def _prob_for(team_id: int | None, probs: list[TeamProbabilities]) -> TeamProbabilities | None:
    if team_id is None:
        return None
    return next((p for p in probs if p.team_id == team_id), None)


def run_simulation(db: Session, request: SimulateRequest) -> SimulateResponse:
    settings = get_settings()
    runs = settings.monte_carlo_runs
    teams, matches = load_state(db)

    # 1. Merge an explicit scenario with anything parsed from the natural-language query.
    scenario: list[ScenarioMatch] = list(request.scenario)
    focus_id = request.focus_team_id
    parsed_desc: str | None = None
    if request.query:
        parsed = smart_parse(request.query, teams, matches)
        parsed_desc = parsed.description
        if focus_id is None:
            focus_id = parsed.focus_team_id
        existing = {s.match_id for s in scenario}
        scenario.extend(s for s in parsed.scenario if s.match_id not in existing)

    # 2. Validate.
    bad = unknown_match_ids(matches, scenario)
    if bad:
        raise SimulationError(f"Unknown match_id(s): {bad}")

    # 3. Apply scenario and recompute standings.
    after_matches = apply_scenario(matches, scenario)
    after_tables = compute_all_tables(teams, after_matches)

    # 4. Probabilities before (current) and after (scenario).
    before_probs = probabilities_for(teams, matches, runs)
    after_probs = (
        probabilities_for(teams, after_matches, runs) if scenario else before_probs
    )

    # 5. Knockout projection for the focus team (post-scenario).
    knockout = project_path(teams, after_matches, focus_id) if focus_id else None

    # 6. AI / template explanation.
    ai_summary = ""
    if focus_id is not None:
        focus_team = next((t for t in teams if t["team_id"] == focus_id), None)
        before = _prob_for(focus_id, before_probs)
        after = _prob_for(focus_id, after_probs)
        next_opp = knockout.rounds[0].opponent if knockout and knockout.rounds else None
        ctx = ExplanationContext(
            team=focus_team["name"] if focus_team else "The team",
            group_name=focus_team["group_name"] if focus_team else "",
            scenario_description=parsed_desc
            or (request.query or _describe_scenario(scenario, teams, matches)),
            before_qualification=before.qualification_probability if before else None,
            after_qualification=after.qualification_probability if after else None,
            next_opponent=next_opp,
            championship_probability=after.championship_probability if after else None,
        )
        ai_summary = generate_explanation(ctx)

    response = SimulateResponse(
        parsed_query=parsed_desc,
        applied_scenario=scenario,
        updated_standings=_tables_to_groups(after_tables),
        qualification_probabilities=after_probs,
        knockout_path=knockout,
        ai_summary=ai_summary,
    )

    # 7. Persist history (best-effort).
    try:
        SimulationRepository(db).save(
            user_input=request.query or json.dumps([s.model_dump() for s in scenario]),
            simulation_result=response.model_dump_json(),
        )
    except Exception:  # noqa: BLE001 - history is non-critical
        db.rollback()

    return response


def _describe_scenario(
    scenario: list[ScenarioMatch], teams: list[dict], matches: list[dict]
) -> str:
    if not scenario:
        return "current situation"
    by_id = {t["team_id"]: t["name"] for t in teams}
    match_by_id = {m["match_id"]: m for m in matches}
    parts = []
    for s in scenario:
        m = match_by_id.get(s.match_id)
        if not m:
            continue
        parts.append(
            f"{by_id.get(m['home_team_id'], '?')} {s.home_goals}-{s.away_goals} "
            f"{by_id.get(m['away_team_id'], '?')}"
        )
    return "; ".join(parts) or "current situation"
