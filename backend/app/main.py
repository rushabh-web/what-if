"""FastAPI application entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.providers import get_provider
from app.repositories import MatchRepository, TeamRepository
from app.routers import groups, matches, share_card, simulate, standings, teams

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database() -> None:
    """Create tables and load teams/matches from the configured provider if empty."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        team_repo = TeamRepository(db)
        if team_repo.count() > 0:
            logger.info("Database already seeded (%d teams)", team_repo.count())
            return
        provider = get_provider()
        teams = provider.get_teams()
        match_rows = provider.get_matches()
        team_repo.bulk_insert(teams)
        MatchRepository(db).bulk_insert(match_rows)
        logger.info("Seeded %d teams and %d matches", len(teams), len(match_rows))
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_database()
    yield


app = FastAPI(
    title="What-If FIFA World Cup 2026 Simulator API",
    version="0.1.0",
    description="Scenario simulation, qualification probabilities, knockout paths "
    "and AI explanations for the FIFA World Cup 2026.",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (teams, groups, matches, standings, simulate, share_card):
    app.include_router(module.router)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "name": "What-If FIFA World Cup 2026 Simulator API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}
