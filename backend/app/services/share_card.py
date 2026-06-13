"""Generate a social-media share card (PNG) for a scenario."""
from __future__ import annotations

import io

from PIL import Image, ImageDraw, ImageFont

from app.schemas.simulation import ShareCardRequest

W, H = 1200, 630  # Twitter/OG card dimensions
BG = (11, 18, 32)
ACCENT = (34, 197, 94)
ACCENT_DOWN = (239, 68, 68)
WHITE = (237, 242, 247)
MUTED = (148, 163, 184)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Best-effort system font with a graceful fallback to Pillow's default."""
    candidates = (
        ["arialbd.ttf", "DejaVuSans-Bold.ttf"] if bold else ["arial.ttf", "DejaVuSans.ttf"]
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _pct(x: float) -> str:
    return f"{round(x * 100)}%"


def render_share_card(req: ShareCardRequest) -> bytes:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Accent bar
    d.rectangle([0, 0, W, 12], fill=ACCENT)

    d.text((60, 70), req.title, font=_font(48, bold=True), fill=MUTED)
    d.text((60, 140), req.scenario_text, font=_font(64, bold=True), fill=WHITE)

    improved = req.after_probability >= req.before_probability
    arrow_color = ACCENT if improved else ACCENT_DOWN

    d.text((60, 300), f"{req.team} — Qualification", font=_font(40), fill=MUTED)
    line = f"{_pct(req.before_probability)}  →  {_pct(req.after_probability)}"
    d.text((60, 350), line, font=_font(96, bold=True), fill=arrow_color)

    if req.most_likely_opponent:
        d.text(
            (60, 480),
            f"Most likely opponent: {req.most_likely_opponent}",
            font=_font(40),
            fill=WHITE,
        )

    d.text((60, H - 60), "What-If FIFA World Cup 2026 Simulator", font=_font(28), fill=MUTED)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
