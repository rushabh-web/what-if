"""Tests for the scenario simulator and Monte Carlo probability engine."""
from __future__ import annotations

from app.engine.monte_carlo import run_probabilities
from app.engine.simulator import apply_scenario, unknown_match_ids
from app.schemas.match import ScenarioMatch
from app.seed.data import build_matches, build_teams

TEAMS = build_teams()
MATCHES = build_matches(TEAMS)


def test_seed_shape() -> None:
    assert len(TEAMS) == 48
    assert len({t["group_name"] for t in TEAMS}) == 12
    # 12 groups x 6 matches = 72 group fixtures.
    assert len(MATCHES) == 72


def test_apply_scenario_marks_finished() -> None:
    scheduled = next(m for m in MATCHES if m["status"] == "scheduled")
    sm = ScenarioMatch(match_id=scheduled["match_id"], home_goals=3, away_goals=1)
    updated = apply_scenario(MATCHES, [sm])
    changed = next(m for m in updated if m["match_id"] == scheduled["match_id"])
    assert changed["status"] == "finished"
    assert changed["home_goals"] == 3 and changed["away_goals"] == 1
    # Original is untouched (pure function).
    assert scheduled["status"] == "scheduled"


def test_unknown_match_ids() -> None:
    bad = unknown_match_ids(MATCHES, [ScenarioMatch(match_id=99999, home_goals=1, away_goals=0)])
    assert bad == [99999]


def test_probabilities_sum_and_range() -> None:
    probs = run_probabilities(TEAMS, MATCHES, runs=2000, seed=1)
    assert len(probs) == 48
    for p in probs:
        assert 0.0 <= p.qualification_probability <= 1.0
        assert 0.0 <= p.championship_probability <= 1.0
        # Monotonic funnel: reaching a later round is never more likely than an earlier one.
        assert p.championship_probability <= p.final_probability + 1e-9
        assert p.final_probability <= p.semi_final_probability + 1e-9
        assert p.round_of_16_probability <= p.qualification_probability + 1e-9

    # Exactly 32 teams qualify and exactly one champion per simulation, so totals hold.
    assert abs(sum(p.qualification_probability for p in probs) - 32.0) < 0.5
    assert abs(sum(p.championship_probability for p in probs) - 1.0) < 0.05


def test_scenario_changes_probability() -> None:
    # Force Argentina (strong) to lose both remaining games -> qualification drops.
    arg = next(t for t in TEAMS if t["fifa_code"] == "ARG")
    arg_remaining = [
        m
        for m in MATCHES
        if m["status"] == "scheduled"
        and arg["team_id"] in (m["home_team_id"], m["away_team_id"])
    ]
    scenario = []
    for m in arg_remaining:
        if m["home_team_id"] == arg["team_id"]:
            scenario.append(ScenarioMatch(match_id=m["match_id"], home_goals=0, away_goals=3))
        else:
            scenario.append(ScenarioMatch(match_id=m["match_id"], home_goals=3, away_goals=0))
    after = apply_scenario(MATCHES, scenario)

    before_probs = run_probabilities(TEAMS, MATCHES, runs=3000, seed=7)
    after_probs = run_probabilities(TEAMS, after, runs=3000, seed=7)
    before_q = next(p for p in before_probs if p.team_id == arg["team_id"]).qualification_probability
    after_q = next(p for p in after_probs if p.team_id == arg["team_id"]).qualification_probability
    assert after_q < before_q
