"""Business logic for Metric resources."""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.metric import Metric
from app.schemas.metric import MetricCreate


def create_metric(db: Session, metric_in: MetricCreate) -> Metric:
    metric = Metric(
        service_name=metric_in.service_name,
        cpu_usage=metric_in.cpu_usage,
        memory_usage=metric_in.memory_usage,
        disk_usage=metric_in.disk_usage,
        network_usage=metric_in.network_usage,
        api_latency=metric_in.api_latency,
        error_rate=metric_in.error_rate,
        db_connections=metric_in.db_connections,
        timestamp=metric_in.timestamp or datetime.utcnow(),
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def list_metrics(db: Session, service_name: Optional[str] = None, skip: int = 0, limit: int = 200) -> List[Metric]:
    query = db.query(Metric)
    if service_name:
        query = query.filter(Metric.service_name == service_name)
    return query.order_by(Metric.timestamp.desc()).offset(skip).limit(limit).all()


def latest_metrics(db: Session, limit_per_service: int = 1) -> List[Metric]:
    """Return the most recent metric for each service."""
    services = [row[0] for row in db.query(Metric.service_name).distinct().all()]
    results = []
    for service_name in services:
        rows = (
            db.query(Metric)
            .filter(Metric.service_name == service_name)
            .order_by(Metric.timestamp.desc())
            .limit(limit_per_service)
            .all()
        )
        results.extend(rows)
    return results


def get_metrics_for_service(db: Session, service_name: str, since: datetime, limit: int = 500) -> List[Metric]:
    return (
        db.query(Metric)
        .filter(Metric.service_name == service_name, Metric.timestamp >= since)
        .order_by(Metric.timestamp.asc())
        .limit(limit)
        .all()
    )


def get_historical_metrics(db: Session, service_name: str, before: datetime, lookback_hours: int = 48, limit: int = 500) -> List[Metric]:
    since = before - timedelta(hours=lookback_hours)
    return (
        db.query(Metric)
        .filter(Metric.service_name == service_name, Metric.timestamp >= since, Metric.timestamp < before)
        .order_by(Metric.timestamp.asc())
        .limit(limit)
        .all()
    )
