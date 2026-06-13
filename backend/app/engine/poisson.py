"""Match Simulation Model — Version 1: Poisson distribution.

Architecture is modular: a future Elo (v2) or SPI/xG (v3) model can replace these
functions without changing the simulation or probability engines.
"""
from __future__ import annotations

LEAGUE_AVG_GOALS = 1.35
HOME_ADVANTAGE = 40.0  # rating points added to the home side


def expected_goals(attack_rating: float, defense_rating: float, home_adv: float = 0.0) -> float:
    """Expected goals for an attack of `attack_rating` vs a defense of `defense_rating`."""
    diff = (attack_rating - defense_rating + home_adv) / 600.0
    return max(0.15, LEAGUE_AVG_GOALS * (10**diff))


def match_expected_goals(
    home_rating: float, away_rating: float, neutral: bool = True
) -> tuple[float, float]:
    """Return (home_xg, away_xg). Group games at a World Cup are effectively neutral."""
    adv = 0.0 if neutral else HOME_ADVANTAGE
    return (
        expected_goals(home_rating, away_rating, home_adv=adv),
        expected_goals(away_rating, home_rating),
    )


def elo_win_probability(rating_a: float, rating_b: float) -> float:
    """Probability that A beats B in a single knockout tie (Elo logistic)."""
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))
