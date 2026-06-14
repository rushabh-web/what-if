"""Natural-language query parsing.

`smart_parse` uses Gemini for intent parsing when a key is configured (handles
explicit scorelines and separate "change X / report on Y" questions), and falls
back to the deterministic rule-based parser otherwise or on any error.
"""
from __future__ import annotations

import logging

from app.config import get_settings
from app.nlp.parser import ParsedQuery, parse_query

logger = logging.getLogger(__name__)

__all__ = ["ParsedQuery", "parse_query", "smart_parse"]


def smart_parse(query: str, teams: list[dict], matches: list[dict]) -> ParsedQuery:
    settings = get_settings()
    if settings.gemini_api_key:
        try:
            from app.nlp.llm_parser import parse_query_llm

            result = parse_query_llm(
                query, teams, matches, settings.gemini_api_key, settings.gemini_model
            )
            # If the LLM found nothing usable, fall back to rules for a best effort.
            if result.scenario or result.focus_team_id is not None:
                return result
        except Exception as exc:  # noqa: BLE001 - fall back rather than fail
            logger.warning("LLM query parse failed (%s); using rule-based parser", exc)
    return parse_query(query, teams, matches)
