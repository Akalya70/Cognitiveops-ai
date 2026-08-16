"""Analysis service: bridges incidents/services/logs/metrics/deployments with the AI engine."""
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.deployment import Deployment
from app.ai.model_manager import model_manager
from app.services import metric_service, log_service, incident_service


def _model_to_dict(obj) -> Dict[str, Any]:
    """Convert a SQLAlchemy model instance into a plain dict."""
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def run_analysis_for_incident(db: Session, incident: Incident, window_minutes: int = 30) -> Dict[str, Any]:
    """Run the full AI analysis pipeline for a given incident and persist results."""
    service_name = incident.affected_service
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)

    current_metrics = [
        _model_to_dict(m) for m in metric_service.get_metrics_for_service(db, service_name, window_start)
    ]
    historical_metrics = [
        _model_to_dict(m)
        for m in metric_service.get_historical_metrics(db, service_name, window_start, lookback_hours=72)
    ]
    logs = [
        _model_to_dict(l) for l in log_service.get_logs_for_service(db, service_name, window_start - timedelta(hours=1))
    ]
    deployments = [
        _model_to_dict(d)
        for d in db.query(Deployment)
        .filter(Deployment.service_name == service_name, Deployment.timestamp >= window_start - timedelta(hours=6))
        .order_by(Deployment.timestamp.asc())
        .all()
    ]
    recent_incidents = [
        incident_service.serialize_incident(i)
        for i in incident_service.list_incidents(db, affected_service=service_name, limit=5)
    ]

    affected_services_count = len({service_name})

    result = model_manager.analyze(
        service_name=service_name,
        current_metrics=current_metrics or [_model_to_dict(m) for m in metric_service.list_metrics(db, service_name, limit=10)],
        historical_metrics=historical_metrics,
        logs=logs or [_model_to_dict(l) for l in log_service.list_logs(db, service_name=service_name, limit=50)],
        deployments=deployments or [_model_to_dict(d) for d in db.query(Deployment).filter(Deployment.service_name == service_name).order_by(Deployment.timestamp.desc()).limit(3).all()],
        recent_incidents=recent_incidents,
        affected_services_count=affected_services_count,
        window_minutes=window_minutes,
    )

    incident_service.apply_analysis_result(db, incident, result)
    return result
