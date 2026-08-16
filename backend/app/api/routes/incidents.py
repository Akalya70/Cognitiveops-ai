"""Incident resource endpoints, including AI analysis trigger and resolution."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.incident import IncidentOut, IncidentCreate, IncidentUpdate, IncidentAnalysisResult
from app.services import incident_service, analysis_service

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])


@router.get("", response_model=List[dict], summary="List incidents with optional filters")
def list_incidents(
    status: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    service: Optional[str] = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    incidents = incident_service.list_incidents(db, status=status, severity=severity, affected_service=service, skip=skip, limit=limit)
    return [incident_service.serialize_incident(i) for i in incidents]


@router.get("/{incident_id}", response_model=dict, summary="Get incident details by ID")
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident_service.serialize_incident(incident)


@router.post("", response_model=dict, status_code=201, summary="Create a new incident")
def create_incident(incident_in: IncidentCreate, db: Session = Depends(get_db)):
    incident = incident_service.create_incident(db, incident_in)
    return incident_service.serialize_incident(incident)


@router.put("/{incident_id}", response_model=dict, summary="Update an incident")
def update_incident(incident_id: int, incident_in: IncidentUpdate, db: Session = Depends(get_db)):
    incident = incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident = incident_service.update_incident(db, incident, incident_in)
    return incident_service.serialize_incident(incident)


@router.delete("/{incident_id}", status_code=204, summary="Delete an incident")
def delete_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident_service.delete_incident(db, incident)
    return None


@router.post("/{incident_id}/analyze", response_model=dict, summary="Run AI root cause analysis on an incident")
def analyze_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    result = analysis_service.run_analysis_for_incident(db, incident)
    return {"incident_id": incident_id, **result}


@router.post("/{incident_id}/resolve", response_model=dict, summary="Mark an incident as resolved")
def resolve_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = incident_service.get_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident = incident_service.resolve_incident(db, incident)
    return incident_service.serialize_incident(incident)
