"""Tests for the standings engine and FIFA tie-break rules."""
from __future__ import annotations

from app.engine.standings import compute_group_table


def _teams() -> list[dict]:
    return [
        {"team_id": 1, "name": "Alpha", "fifa_code": "ALP", "group_name": "A", "rating": 1800},
        {"team_id": 2, "name": "Bravo", "fifa_code": "BRA", "group_name": "A", "rating": 1700},
        {"team_id": 3, "name": "Charlie", "fifa_code": "CHA", "group_name": "A", "rating": 1600},
        {"team_id": 4, "name": "Delta", "fifa_code": "DEL", "group_name": "A", "rating": 1500},
    ]


def _match(mid, h, a, hg, ag) -> dict:
    return {
        "match_id": mid,
        "home_team_id": h,
        "away_team_id": a,
        "group_name": "A",
        "matchday": 1,
        "status": "finished",
        "home_goals": hg,
        "away_goals": ag,
    }


def test_points_and_order() -> None:
    # Alpha wins both, Bravo wins one, Charlie/Delta lose.
    matches = [
        _match(1, 1, 2, 2, 0),  # Alpha beats Bravo
        _match(2, 3, 4, 1, 1),  # Charlie draws Delta
        _match(3, 1, 3, 3, 0),  # Alpha beats Charlie
        _match(4, 2, 4, 1, 0),  # Bravo beats Delta
    ]
    table = compute_group_table("A", _teams(), matches)
    # Alpha 6pts; Bravo 3pts; then Delta (GD -1) above Charlie (GD -3) on goal difference.
    assert [r.team_id for r in table] == [1, 2, 4, 3]
    assert table[0].points == 6
    assert table[0].qualification_status == "qualified"
    assert table[1].qualification_status == "qualified"
    assert table[2].qualification_status == "third"
    assert table[3].qualification_status == "out"


def test_goal_difference_tiebreak() -> None:
    # Alpha and Bravo both win their first game; Alpha has better GD.
    matches = [
        _match(1, 1, 3, 4, 0),  # Alpha +4
        _match(2, 2, 4, 1, 0),  # Bravo +1
    ]
    table = compute_group_table("A", _teams(), matches)
    assert table[0].team_id == 1  # Alpha ahead on GD
    assert table[1].team_id == 2


def test_head_to_head_breaks_equal_record() -> None:
    # Alpha and Bravo identical on points/GD/GF, but Alpha beat Bravo head-to-head.
    matches = [
        _match(1, 1, 2, 1, 0),  # Alpha beats Bravo (H2H)
        _match(2, 1, 3, 0, 1),  # Alpha loses to Charlie
        _match(3, 2, 4, 0, 1),  # Bravo loses to Delta
    ]
    # Alpha: 1 win 1 loss, GF1 GA1 -> 3 pts. Bravo: 1 win 1 loss GF0 GA1 -> 3 pts.
    table = compute_group_table("A", _teams(), matches)
    alpha = next(r for r in table if r.team_id == 1)
    bravo = next(r for r in table if r.team_id == 2)
    assert alpha.position < bravo.position
