"""Standings endpoints (computed from current match results)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.engine.standings import compute_all_tables, compute_group_table
from app.schemas.simulation import GroupTable
from app.services.state import load_state

router = APIRouter(tags=["standings"])


@router.get("/standings", response_model=list[GroupTable])
def get_standings(db: Session = Depends(get_db)) -> list[GroupTable]:
    teams, matches = load_state(db)
    tables = compute_all_tables(teams, matches)
    return [GroupTable(group_name=g, rows=rows) for g, rows in sorted(tables.items())]


@router.get("/standings/{group_name}", response_model=GroupTable)
def get_group_standings(group_name: str, db: Session = Depends(get_db)) -> GroupTable:
    teams, matches = load_state(db)
    group_name = group_name.upper()
    if not any(t["group_name"] == group_name for t in teams):
        raise HTTPException(status_code=404, detail="Group not found")
    rows = compute_group_table(group_name, teams, matches)
    return GroupTable(group_name=group_name, rows=rows)
