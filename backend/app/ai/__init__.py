"""AI explanation layer. Generates narrative only — never computes results."""
from app.ai.explainer import ExplanationContext, generate_explanation

__all__ = ["ExplanationContext", "generate_explanation"]
