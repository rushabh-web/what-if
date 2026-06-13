"""Knockout bracket: seeding, deterministic projected path, shared by Monte Carlo.

The 48-team format sends the 12 group winners, 12 runners-up and the 8 best
third-placed teams to a Round of 32. Seeding here is a faithful approximation:
group winners are seeded above runners-up above third-placed teams, and within
each tier by rating. Favourites advance for the *deterministic* projected route;
the Monte Carlo engine samples each tie instead.
"""
from __future__ import annotations

from app.engine.poisson import elo_win_probability
from app.engine.standings import compute_all_tables
from app.schemas.knockout import KnockoutPath, KnockoutRound

ROUND_NAMES = ["Round of 32", "Round of 16", "Quarter Final", "Semi Final", "Final"]


def seed_positions(n: int) -> list[int]:
    """Standard single-elimination bracket slot order for `n` seeds (n a power of 2)."""
    order = [0]
    while len(order) < n:
        m = len(order) * 2
        nxt: list[int] = []
        for s in order:
            nxt.append(s)
            nxt.append(m - 1 - s)
        order = nxt
    return order


def _resolve_expected(matches: list[dict], rating: dict[int, float]) -> list[dict]:
    """Return a copy of matches with every unplayed game resolved to its expected result."""
    from app.engine.poisson import match_expected_goals

    resolved: list[dict] = []
    for m in matches:
        m = dict(m)
        if m.get("status") != "finished" or m.get("home_goals") is None:
            hx, ax = match_expected_goals(
                rating.get(m["home_team_id"], 1500), rating.get(m["away_team_id"], 1500)
            )
            hg, ag = round(hx), round(ax)
            if hg == ag:  # break expected draws toward the stronger side
                if rating.get(m["home_team_id"], 0) >= rating.get(m["away_team_id"], 0):
                    hg += 1
                else:
                    ag += 1
            m["home_goals"], m["away_goals"], m["status"] = hg, ag, "finished"
        resolved.append(m)
    return resolved


def _best_thirds(tables: dict[str, list]) -> list[tuple]:
    """Return the 8 best third-placed (group, team_id) tuples, FIFA-ranked."""
    thirds = []
    for g, rows in tables.items():
        if len(rows) >= 3:
            r = rows[2]
            thirds.append((r.points, r.gd, r.gf, r.rating if hasattr(r, "rating") else 0, r))
    thirds.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    return [(t[4].group_name, t[4].team_id) for t in thirds[:8]]


def build_seeded_bracket(
    teams: list[dict], matches: list[dict]
) -> tuple[list[int], dict[int, str]]:
    """Build the 32-slot bracket (team_ids in slot order) from expected final standings.

    Returns (bracket_slots, seed_label) where seed_label maps team_id -> e.g. "1A".
    """
    rating = {t["team_id"]: float(t.get("rating", 1500)) for t in teams}
    resolved = _resolve_expected(matches, rating)
    tables = compute_all_tables(teams, resolved)

    seed_label: dict[int, str] = {}
    winners: list[int] = []
    runners: list[int] = []
    for g, rows in tables.items():
        if rows:
            winners.append(rows[0].team_id)
            seed_label[rows[0].team_id] = f"1{g}"
        if len(rows) > 1:
            runners.append(rows[1].team_id)
            seed_label[rows[1].team_id] = f"2{g}"
    thirds = _best_thirds(tables)
    third_ids = []
    for g, tid in thirds:
        third_ids.append(tid)
        seed_label[tid] = f"3{g}"

    # Seed tiers: winners, then runners-up, then thirds; within a tier by rating.
    winners.sort(key=lambda t: rating[t], reverse=True)
    runners.sort(key=lambda t: rating[t], reverse=True)
    third_ids.sort(key=lambda t: rating[t], reverse=True)
    seedlist = winners + runners + third_ids  # best -> worst, 32 entries

    positions = seed_positions(len(seedlist))
    slots = [0] * len(seedlist)
    for seed_idx, slot_idx in enumerate(positions):
        slots[slot_idx] = seedlist[seed_idx]
    return slots, seed_label


def project_path(teams: list[dict], matches: list[dict], focus_team_id: int) -> KnockoutPath | None:
    """Deterministic projected knockout route for `focus_team_id` (favourites advance)."""
    rating = {t["team_id"]: float(t.get("rating", 1500)) for t in teams}
    name = {t["team_id"]: t["name"] for t in teams}
    code = {t["team_id"]: t["fifa_code"] for t in teams}

    slots, seed_label = build_seeded_bracket(teams, matches)
    if focus_team_id not in slots:
        # Team did not reach the projected knockout stage.
        return KnockoutPath(
            team_id=focus_team_id,
            team=name.get(focus_team_id, "Unknown"),
            seeded_position=seed_label.get(focus_team_id, "—"),
            rounds=[],
        )

    idx = slots.index(focus_team_id)
    rounds: list[KnockoutRound] = []
    for r, round_name in enumerate(ROUND_NAMES):
        block = 1 << r  # size of current consolidated block
        start = (idx // block) * block
        sibling_start = start + block if (start // block) % 2 == 0 else start - block
        sibling_slots = slots[sibling_start : sibling_start + block]
        # Projected opponent = strongest team in the sibling block (favourites advance).
        opponents = [t for t in sibling_slots if t in rating]
        if not opponents:
            break
        opp = max(opponents, key=lambda t: rating[t])
        rounds.append(
            KnockoutRound(
                round_name=round_name,
                opponent_team_id=opp,
                opponent=name.get(opp, "TBD"),
                opponent_code=code.get(opp, ""),
                win_probability=round(elo_win_probability(rating[focus_team_id], rating[opp]), 3),
            )
        )
    return KnockoutPath(
        team_id=focus_team_id,
        team=name.get(focus_team_id, "Unknown"),
        seeded_position=seed_label.get(focus_team_id, "—"),
        rounds=rounds,
    )
