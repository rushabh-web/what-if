"""Probability Engine — Monte Carlo simulation of the remaining tournament.

Simulates the remaining group matches (Poisson model) and the full knockout
bracket many times to estimate, per team: qualification, group win, and the
probability of reaching each knockout round through to the championship.

Vectorised with numpy across all simulations. The group-stage ordering inside
the hot loop uses (points, GD, GF, rating) — head-to-head ties are not resolved
here for speed; the *displayed* standings use the full FIFA tie-break chain.
"""
from __future__ import annotations

import numpy as np

from app.engine.knockout import seed_positions
from app.engine.poisson import match_expected_goals
from app.schemas.probability import TeamProbabilities


def _finished(m: dict) -> bool:
    return m.get("status") == "finished" and m.get("home_goals") is not None


def run_probabilities(
    teams: list[dict], matches: list[dict], runs: int = 10000, seed: int = 12345
) -> list[TeamProbabilities]:
    rng = np.random.default_rng(seed)
    n = runs

    rating = {t["team_id"]: float(t.get("rating", 1500)) for t in teams}
    name = {t["team_id"]: t["name"] for t in teams}
    code = {t["team_id"]: t["fifa_code"] for t in teams}
    group_of = {t["team_id"]: t["group_name"] for t in teams}
    max_id = max(rating) + 1
    rating_arr = np.full(max_id, 1500.0)
    for tid, r in rating.items():
        rating_arr[tid] = r

    groups = sorted({t["group_name"] for t in teams})

    # Per-group winner / runner / third arrays across all sims.
    winners = np.zeros((n, len(groups)), dtype=np.int32)
    runners = np.zeros((n, len(groups)), dtype=np.int32)
    thirds = np.zeros((n, len(groups)), dtype=np.int32)
    thirds_score = np.zeros((n, len(groups)), dtype=np.float64)

    for gi, g in enumerate(groups):
        members = sorted(
            (t["team_id"] for t in teams if t["group_name"] == g),
        )
        local = {tid: i for i, tid in enumerate(members)}
        m_arr = np.array(members)

        base_pts = np.zeros(4, dtype=np.int64)
        base_gd = np.zeros(4, dtype=np.int64)
        base_gf = np.zeros(4, dtype=np.int64)
        remaining: list[tuple[int, int, float, float]] = []
        for m in matches:
            if m["group_name"] != g:
                continue
            lh, la = local[m["home_team_id"]], local[m["away_team_id"]]
            if _finished(m):
                hg, ag = m["home_goals"], m["away_goals"]
                _apply(base_pts, base_gd, base_gf, lh, la, hg, ag)
            else:
                hx, ax = match_expected_goals(
                    rating[m["home_team_id"]], rating[m["away_team_id"]]
                )
                remaining.append((lh, la, hx, ax))

        pts = np.repeat(base_pts[None, :], n, axis=0)
        gd = np.repeat(base_gd[None, :], n, axis=0)
        gf = np.repeat(base_gf[None, :], n, axis=0)
        for lh, la, hx, ax in remaining:
            hg = rng.poisson(hx, n)
            ag = rng.poisson(ax, n)
            home_pts = np.where(hg > ag, 3, np.where(hg == ag, 1, 0))
            away_pts = np.where(ag > hg, 3, np.where(hg == ag, 1, 0))
            pts[:, lh] += home_pts
            pts[:, la] += away_pts
            gd[:, lh] += hg - ag
            gd[:, la] += ag - hg
            gf[:, lh] += hg
            gf[:, la] += ag

        local_rating = np.array([rating[tid] for tid in members])
        score = (
            pts * 1_000_000.0
            + (gd + 100) * 1_000.0
            + gf
            + local_rating[None, :] * 1e-6
        )
        order = np.argsort(-score, axis=1)  # best -> worst local indices
        winners[:, gi] = m_arr[order[:, 0]]
        runners[:, gi] = m_arr[order[:, 1]]
        thirds[:, gi] = m_arr[order[:, 2]]
        thirds_score[:, gi] = np.take_along_axis(score, order[:, 2:3], axis=1)[:, 0]

    # Best 8 of the 12 third-placed teams advance.
    third_order = np.argsort(-thirds_score, axis=1)
    q_thirds = np.take_along_axis(thirds, third_order[:, :8], axis=1)  # (n, 8)

    # Counters indexed by team_id.
    qual = np.zeros(max_id, dtype=np.int64)
    grp_win = np.zeros(max_id, dtype=np.int64)
    reach_r16 = np.zeros(max_id, dtype=np.int64)
    reach_qf = np.zeros(max_id, dtype=np.int64)
    reach_sf = np.zeros(max_id, dtype=np.int64)
    reach_final = np.zeros(max_id, dtype=np.int64)
    champ = np.zeros(max_id, dtype=np.int64)

    np.add.at(grp_win, winners.ravel(), 1)
    qualifiers = np.concatenate([winners, runners, q_thirds], axis=1)  # (n, 32)
    np.add.at(qual, qualifiers.ravel(), 1)

    # Seed the 32 qualifiers into the bracket: winners > runners > thirds, then rating.
    bonus = np.concatenate(
        [np.full(12, 400.0), np.full(12, 200.0), np.full(8, 0.0)]
    )
    q_ratings = rating_arr[qualifiers]
    seed_score = q_ratings + bonus[None, :]
    seed_order = np.argsort(-seed_score, axis=1)  # best -> worst seed
    seedlist = np.take_along_axis(qualifiers, seed_order, axis=1)  # (n, 32)

    positions = seed_positions(32)
    inv = np.empty(32, dtype=np.int64)
    for rank, slot in enumerate(positions):
        inv[slot] = rank
    bracket = seedlist[:, inv]  # team_ids in bracket slot order

    # Play out the knockout rounds; winners advance, accumulating reach counters.
    reach_counters = [reach_r16, reach_qf, reach_sf, reach_final, champ]
    current = bracket
    for r in range(5):
        cur_r = rating_arr[current]
        pairs = current.reshape(n, -1, 2)
        pr = cur_r.reshape(n, -1, 2)
        a_id, b_id = pairs[:, :, 0], pairs[:, :, 1]
        a_r, b_r = pr[:, :, 0], pr[:, :, 1]
        p_a = 1.0 / (1.0 + 10 ** ((b_r - a_r) / 400.0))
        a_wins = rng.random((n, pairs.shape[1])) < p_a
        winner = np.where(a_wins, a_id, b_id)
        np.add.at(reach_counters[r], winner.ravel(), 1)
        current = winner

    out: list[TeamProbabilities] = []
    for tid in sorted(rating):
        out.append(
            TeamProbabilities(
                team_id=tid,
                team=name[tid],
                fifa_code=code[tid],
                group_name=group_of[tid],
                qualification_probability=round(qual[tid] / n, 4),
                group_win_probability=round(grp_win[tid] / n, 4),
                round_of_16_probability=round(reach_r16[tid] / n, 4),
                quarter_final_probability=round(reach_qf[tid] / n, 4),
                semi_final_probability=round(reach_sf[tid] / n, 4),
                final_probability=round(reach_final[tid] / n, 4),
                championship_probability=round(champ[tid] / n, 4),
            )
        )
    return out


def _apply(pts, gd, gf, lh: int, la: int, hg: int, ag: int) -> None:
    if hg > ag:
        pts[lh] += 3
    elif hg < ag:
        pts[la] += 3
    else:
        pts[lh] += 1
        pts[la] += 1
    gd[lh] += hg - ag
    gd[la] += ag - hg
    gf[lh] += hg
    gf[la] += ag
