"""Ad-hoc analysis endpoint - run the AI pipeline for a service without creating an incident."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ai.model_manager import model_manager
from app.services import metric_service, log_service
from app.models.deployment import Deployment

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.get("/service/{service_name}", summary="Run ad-hoc root cause analysis for a service")
def analyze_service(service_name: str, window_minutes: int = Query(default=30), db: Session = Depends(get_db)):
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)

    current_metrics = [
        {c.name: getattr(m, c.name) for c in m.__table__.columns}
        for m in metric_service.get_metrics_for_service(db, service_name, window_start)
    ]
    historical_metrics = [
        {c.name: getattr(m, c.name) for c in m.__table__.columns}
        for m in metric_service.get_historical_metrics(db, service_name, window_start, lookback_hours=72)
    ]
    logs = [
        {c.name: getattr(l, c.name) for c in l.__table__.columns}
        for l in log_service.get_logs_for_service(db, service_name, window_start - timedelta(hours=1))
    ]
    deployments = [
        {c.name: getattr(d, c.name) for c in d.__table__.columns}
        for d in db.query(Deployment)
        .filter(Deployment.service_name == service_name, Deployment.timestamp >= window_start - timedelta(hours=6))
        .all()
    ]

    result = model_manager.analyze(
        service_name=service_name,
        current_metrics=current_metrics,
        historical_metrics=historical_metrics,
        logs=logs,
        deployments=deployments,
        recent_incidents=[],
        window_minutes=window_minutes,
    )
    return {"service_name": service_name, **result}
