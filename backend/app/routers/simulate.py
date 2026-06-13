"""Scenario simulation endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.simulation import SimulateRequest, SimulateResponse
from app.services.simulation_service import SimulationError, run_simulation

router = APIRouter(tags=["simulate"])


@router.post("/simulate", response_model=SimulateResponse)
def simulate(request: SimulateRequest, db: Session = Depends(get_db)) -> SimulateResponse:
    try:
        return run_simulation(db, request)
    except SimulationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
