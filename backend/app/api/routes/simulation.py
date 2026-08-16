"""Simulation endpoints used to drive the hackathon demo flow."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import simulation_service

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])


@router.post("/normal", summary="Simulate a healthy baseline system")
def simulate_normal(db: Session = Depends(get_db)):
    return simulation_service.simulate_normal(db)


@router.post("/database-failure", summary="Simulate a database connection exhaustion incident")
def simulate_database_failure(db: Session = Depends(get_db)):
    return simulation_service.simulate_database_failure(db)


@router.post("/memory-overload", summary="Simulate a memory overload incident")
def simulate_memory_overload(db: Session = Depends(get_db)):
    return simulation_service.simulate_memory_overload(db)


@router.post("/bad-deployment", summary="Simulate a bad deployment incident")
def simulate_bad_deployment(db: Session = Depends(get_db)):
    return simulation_service.simulate_bad_deployment(db)


@router.post("/network-failure", summary="Simulate a network failure incident")
def simulate_network_failure(db: Session = Depends(get_db)):
    return simulation_service.simulate_network_failure(db)


@router.post("/api-timeout", summary="Simulate an API timeout incident")
def simulate_api_timeout(db: Session = Depends(get_db)):
    return simulation_service.simulate_api_timeout(db)
