"""Simulation history repository."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.simulation import Simulation


class SimulationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, user_input: str, simulation_result: str) -> Simulation:
        row = Simulation(user_input=user_input, simulation_result=simulation_result)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
