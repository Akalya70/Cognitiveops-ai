"""Metric resource endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.metric import MetricOut, MetricCreate
from app.services import metric_service

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])


@router.get("", response_model=List[MetricOut], summary="List metrics with optional service filter")
def list_metrics(
    service: Optional[str] = Query(default=None),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    return metric_service.list_metrics(db, service_name=service, skip=skip, limit=limit)


@router.post("", response_model=MetricOut, status_code=201, summary="Create a metric record")
def create_metric(metric_in: MetricCreate, db: Session = Depends(get_db)):
    return metric_service.create_metric(db, metric_in)


@router.get("/latest", response_model=List[MetricOut], summary="Get the latest metric per service")
def get_latest_metrics(db: Session = Depends(get_db)):
    return metric_service.latest_metrics(db)


@router.get("/{service_name}", response_model=List[MetricOut], summary="Get metrics for a specific service")
def get_metrics_for_service(service_name: str, limit: int = 100, db: Session = Depends(get_db)):
    return metric_service.list_metrics(db, service_name=service_name, limit=limit)
