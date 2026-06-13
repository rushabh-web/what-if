"""Cached Monte Carlo runner.

Monte Carlo is the most expensive operation, so results are memoised by the
exact match-result signature. Identical states (e.g. the current standings, or a
repeated scenario) are computed once per process.
"""
from __future__ import annotations

import hashlib
import json

from cachetools import LRUCache

from app.engine.monte_carlo import run_probabilities
from app.schemas.probability import TeamProbabilities

_cache: LRUCache = LRUCache(maxsize=128)


def _signature(matches: list[dict], runs: int) -> str:
    payload = sorted(
        (m["match_id"], m["status"], m["home_goals"], m["away_goals"]) for m in matches
    )
    raw = json.dumps([runs, payload], default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def probabilities_for(
    teams: list[dict], matches: list[dict], runs: int
) -> list[TeamProbabilities]:
    key = _signature(matches, runs)
    if key in _cache:
        return _cache[key]
    result = run_probabilities(teams, matches, runs=runs)
    _cache[key] = result
    return result
