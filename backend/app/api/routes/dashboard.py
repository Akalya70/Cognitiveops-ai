"""Dashboard summary endpoint aggregating system-wide health metrics."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.service import Service
from app.models.incident import Incident
from app.models.deployment import Deployment
from app.services import metric_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", summary="Get dashboard summary", description="Aggregated counts and health indicators for the whole system.")
def get_summary(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    total_services = len(services)
    healthy_services = len([s for s in services if s.status == "HEALTHY"])
    degraded_services = len([s for s in services if s.status in ("DEGRADED", "CRITICAL")])
    avg_health_score = round(sum(s.health_score for s in services) / total_services, 1) if total_services else 100.0

    active_incidents = db.query(Incident).filter(Incident.status.in_(["OPEN", "INVESTIGATING", "MITIGATED"])).count()
    critical_incidents = db.query(Incident).filter(Incident.severity == "CRITICAL", Incident.status != "RESOLVED").count()

    latest_metrics = metric_service.latest_metrics(db)
    anomaly_count = 0
    from app.ai.anomaly_detector import AnomalyDetector
    detector = AnomalyDetector()
    for m in latest_metrics:
        metric_dict = {c.name: getattr(m, c.name) for c in m.__table__.columns}
        result = detector.score(metric_dict)
        if result["is_anomaly"]:
            anomaly_count += 1

    recent_deployments = (
        db.query(Deployment).order_by(Deployment.timestamp.desc()).limit(5).all()
    )

    return {
        "total_services": total_services,
        "healthy_services": healthy_services,
        "degraded_services": degraded_services,
        "active_incidents": active_incidents,
        "critical_incidents": critical_incidents,
        "average_health_score": avg_health_score,
        "anomaly_count": anomaly_count,
        "recent_deployments": [
            {
                "id": d.id,
                "service_name": d.service_name,
                "version": d.version,
                "status": d.status,
                "timestamp": d.timestamp,
            }
            for d in recent_deployments
        ],
    }
