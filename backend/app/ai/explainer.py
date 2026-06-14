"""Explanation generation: Anthropic (Claude) when configured, else template.

This layer is strictly explanatory. All numbers it receives are pre-computed by
the deterministic engines; the model is asked only to narrate them.
"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass

from app.ai.templates import build_template_explanation
from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class ExplanationContext:
    team: str
    group_name: str = ""
    scenario_description: str = ""
    before_qualification: float | None = None
    after_qualification: float | None = None
    next_opponent: str | None = None
    championship_probability: float | None = None


_SYSTEM = (
    "You are a football tournament analyst for a FIFA World Cup what-if simulator. "
    "You are given pre-computed standings and probabilities. Write a single concise "
    "explanation of 100-200 words. Never invent or recompute numbers — only use the "
    "values provided. Be clear, neutral and engaging. Do not use markdown."
)


def _build_prompt(ctx: ExplanationContext) -> str:
    def pct(x: float | None) -> str:
        return "n/a" if x is None else f"{round(x * 100)}%"

    return (
        f"Team: {ctx.team} (Group {ctx.group_name})\n"
        f"Scenario: {ctx.scenario_description or 'current situation'}\n"
        f"Qualification probability before: {pct(ctx.before_qualification)}\n"
        f"Qualification probability after: {pct(ctx.after_qualification)}\n"
        f"Projected next knockout opponent: {ctx.next_opponent or 'TBD'}\n"
        f"Championship probability: {pct(ctx.championship_probability)}\n\n"
        "Write the explanation now."
    )


def generate_explanation(ctx: ExplanationContext) -> str:
    settings = get_settings()
    if settings.gemini_api_key:
        try:
            return _gemini_explanation(ctx, settings.gemini_api_key, settings.gemini_model)
        except Exception as exc:  # noqa: BLE001 - never fail the request over the narrative
            logger.warning("Gemini explanation failed (%s); using template", exc)
    elif settings.anthropic_api_key:
        try:
            return _anthropic_explanation(ctx, settings.anthropic_api_key, settings.anthropic_model)
        except Exception as exc:  # noqa: BLE001 - never fail the request over the narrative
            logger.warning("Anthropic explanation failed (%s); using template", exc)
    return build_template_explanation(asdict(ctx))


def _gemini_explanation(ctx: ExplanationContext, api_key: str, model: str) -> str:
    import httpx

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": _SYSTEM}]},
        "contents": [{"parts": [{"text": _build_prompt(ctx)}]}],
        "generationConfig": {
            "maxOutputTokens": 500,
            "temperature": 0.7,
            # gemini-2.5 "thinks" by default and would eat the output budget; disable it.
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    with httpx.Client(timeout=20.0) as client:
        resp = client.post(
            url,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"Gemini returned no candidates: {data}")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts).strip()
    if not text:
        raise RuntimeError("Gemini returned empty text")
    return text


def _anthropic_explanation(ctx: ExplanationContext, api_key: str, model: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=model,
        max_tokens=400,
        system=_SYSTEM,
        messages=[{"role": "user", "content": _build_prompt(ctx)}],
    )
    return "".join(block.text for block in msg.content if block.type == "text").strip()
