"""Deterministic, no-API-key fallback explanation generator."""
from __future__ import annotations


def _pct(x: float) -> str:
    return f"{round(x * 100)}%"


def build_template_explanation(ctx: dict) -> str:
    team = ctx.get("team", "The team")
    scenario = ctx.get("scenario_description") or "the current situation"
    before = ctx.get("before_qualification")
    after = ctx.get("after_qualification")
    group = ctx.get("group_name", "")
    opponent = ctx.get("next_opponent")
    champ = ctx.get("championship_probability")

    parts: list[str] = []
    parts.append(f"Scenario: {scenario}.")

    if before is not None and after is not None:
        delta = after - before
        if abs(delta) < 0.02:
            parts.append(
                f"{team}'s qualification chances stay roughly level at {_pct(after)} "
                f"(from {_pct(before)} in Group {group})."
            )
        elif delta < 0:
            parts.append(
                f"This is bad news for {team}: their qualification probability drops "
                f"from {_pct(before)} to {_pct(after)}, a swing of {_pct(abs(delta))}."
            )
        else:
            parts.append(
                f"This helps {team}: their qualification probability rises from "
                f"{_pct(before)} to {_pct(after)}, up {_pct(abs(delta))}."
            )
    elif after is not None:
        parts.append(
            f"{team} currently has a {_pct(after)} chance of advancing from Group {group}."
        )

    if opponent:
        parts.append(f"On the projected route they would next meet {opponent}.")
    if champ is not None and champ > 0.005:
        parts.append(f"Their title probability in this scenario is about {_pct(champ)}.")

    parts.append(
        "Remaining group matches still carry significant weight, so the picture can "
        "shift again with each result."
    )
    return " ".join(parts)
