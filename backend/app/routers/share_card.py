"""Share card image endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Response

from app.schemas.simulation import ShareCardRequest
from app.services.share_card import render_share_card

router = APIRouter(tags=["share-card"])


@router.post(
    "/share-card",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
def share_card(request: ShareCardRequest) -> Response:
    png = render_share_card(request)
    return Response(content=png, media_type="image/png")
