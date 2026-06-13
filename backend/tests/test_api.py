"""End-to-end API tests using an isolated SQLite database."""
from __future__ import annotations

import os
import tempfile

import pytest

# Use a throwaway DB file before importing the app/config.
_TMP_DB = os.path.join(tempfile.gettempdir(), "fifa_test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB}"
os.environ["MONTE_CARLO_RUNS"] = "1500"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    if os.path.exists(_TMP_DB):
        os.remove(_TMP_DB)
    with TestClient(app) as c:  # triggers lifespan -> seeding
        yield c


def test_health(client) -> None:
    assert client.get("/health").json()["status"] == "ok"


def test_teams_seeded(client) -> None:
    teams = client.get("/teams").json()
    assert len(teams) == 48


def test_standings(client) -> None:
    standings = client.get("/standings").json()
    assert len(standings) == 12
    for group in standings:
        assert len(group["rows"]) == 4
        assert group["rows"][0]["position"] == 1


def test_matches_filter(client) -> None:
    finished = client.get("/matches", params={"status": "finished"}).json()
    assert all(m["status"] == "finished" for m in finished)
    assert finished[0]["home_team"]  # enriched with names


def test_simulate_natural_language(client) -> None:
    resp = client.post("/simulate", json={"query": "What if Argentina loses today?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["parsed_query"]
    assert len(data["qualification_probabilities"]) == 48
    assert data["ai_summary"]
    assert data["knockout_path"] is not None


def test_simulate_explicit_scenario(client) -> None:
    # Find a scheduled match to override.
    scheduled = client.get("/matches", params={"status": "scheduled"}).json()[0]
    resp = client.post(
        "/simulate",
        json={
            "scenario": [
                {"match_id": scheduled["match_id"], "home_goals": 2, "away_goals": 0}
            ],
            "focus_team_id": scheduled["home_team_id"],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["knockout_path"]["team_id"] == scheduled["home_team_id"]


def test_simulate_unknown_match(client) -> None:
    resp = client.post("/simulate", json={"scenario": [{"match_id": 999999, "home_goals": 1, "away_goals": 0}]})
    assert resp.status_code == 400


def test_share_card(client) -> None:
    resp = client.post(
        "/share-card",
        json={
            "scenario_text": "Argentina loses today",
            "team": "Argentina",
            "before_probability": 0.92,
            "after_probability": 0.61,
            "most_likely_opponent": "Germany",
        },
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert resp.content[:4] == b"\x89PNG"
