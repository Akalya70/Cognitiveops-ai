"""Business logic for Incident resources."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.utils.response_utils import to_json, from_json


def create_incident(db: Session, incident_in: IncidentCreate) -> Incident:
    incident = Incident(
        title=incident_in.title,
        description=incident_in.description,
        severity=incident_in.severity,
        status=incident_in.status,
        affected_service=incident_in.affected_service,
        probable_root_cause=incident_in.probable_root_cause,
        confidence_score=incident_in.confidence_score,
        impact_score=incident_in.impact_score,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def get_incident(db: Session, incident_id: int) -> Optional[Incident]:
    return db.query(Incident).filter(Incident.id == incident_id).first()


def list_incidents(
    db: Session,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    affected_service: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Incident]:
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if affected_service:
        query = query.filter(Incident.affected_service == affected_service)
    return query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()


def update_incident(db: Session, incident: Incident, incident_in: IncidentUpdate) -> Incident:
    update_data = incident_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)
    db.commit()
    db.refresh(incident)
    return incident


def delete_incident(db: Session, incident: Incident) -> None:
    db.delete(incident)
    db.commit()


def resolve_incident(db: Session, incident: Incident) -> Incident:
    incident.status = "RESOLVED"
    incident.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return incident


def apply_analysis_result(db: Session, incident: Incident, analysis: dict) -> Incident:
    """Persist AI analysis output onto an incident record."""
    incident.probable_root_cause = analysis["root_cause"]
    incident.confidence_score = analysis["confidence"]
    incident.severity = analysis["severity"]
    incident.impact_score = analysis["impact_score"]
    incident.evidence = to_json(analysis["evidence"])
    incident.recommendations = to_json(analysis["recommendations"])
    incident.timeline = to_json(analysis["timeline"])
    incident.contributing_factors = to_json(analysis["contributing_factors"])
    if incident.status == "OPEN":
        incident.status = "INVESTIGATING"
    db.commit()
    db.refresh(incident)
    return incident


def serialize_incident(incident: Incident) -> dict:
    """Convert an Incident ORM object to a dict with JSON fields decoded."""
    return {
        "id": incident.id,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": incident.status,
        "affected_service": incident.affected_service,
        "probable_root_cause": incident.probable_root_cause,
        "confidence_score": incident.confidence_score,
        "impact_score": incident.impact_score,
        "created_at": incident.created_at,
        "resolved_at": incident.resolved_at,
        "evidence": from_json(incident.evidence, []),
        "recommendations": from_json(incident.recommendations, []),
        "timeline": from_json(incident.timeline, []),
        "contributing_factors": from_json(incident.contributing_factors, {}),
    }
