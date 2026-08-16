"""Simulation service: generates realistic metrics/logs/deployments/incidents
for each demo scenario, then runs the AI analysis pipeline on the result.
"""
import random
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.metric import Metric
from app.models.log import Log
from app.models.deployment import Deployment
from app.models.incident import Incident
from app.services import analysis_service, incident_service
from app.schemas.incident import IncidentCreate


def _add_metric_series(db: Session, service_name: str, base: Dict[str, float], steps: int, drift: Dict[str, float], start_minutes_ago: int, step_minutes: int = 1):
    """Insert a series of metrics that drift linearly from `base` by `drift` per step."""
    now = datetime.utcnow()
    for i in range(steps):
        ts = now - timedelta(minutes=start_minutes_ago - i * step_minutes)
        metric = Metric(
            service_name=service_name,
            timestamp=ts,
            cpu_usage=max(0, min(100, base["cpu_usage"] + drift["cpu_usage"] * i + random.uniform(-2, 2))),
            memory_usage=max(0, min(100, base["memory_usage"] + drift["memory_usage"] * i + random.uniform(-2, 2))),
            disk_usage=max(0, min(100, base["disk_usage"] + drift["disk_usage"] * i + random.uniform(-1, 1))),
            network_usage=max(0, min(100, base["network_usage"] + drift["network_usage"] * i + random.uniform(-2, 2))),
            api_latency=max(0, base["api_latency"] + drift["api_latency"] * i + random.uniform(-10, 10)),
            error_rate=max(0, min(100, base["error_rate"] + drift["error_rate"] * i + random.uniform(-0.5, 0.5))),
            db_connections=max(0, min(100, base["db_connections"] + drift["db_connections"] * i + random.uniform(-2, 2))),
        )
        db.add(metric)
    db.commit()


def _add_log(db: Session, service_name: str, level: str, message: str, minutes_ago: int, error_code: str = None, trace_id: str = None, source: str = "application"):
    log = Log(
        service_name=service_name,
        level=level,
        message=message,
        source=source,
        error_code=error_code,
        trace_id=trace_id,
        timestamp=datetime.utcnow() - timedelta(minutes=minutes_ago),
    )
    db.add(log)
    db.commit()


def _add_deployment(db: Session, service_name: str, version: str, minutes_ago: int, status: str = "SUCCESS", description: str = ""):
    deployment = Deployment(
        service_name=service_name,
        version=version,
        environment="production",
        deployed_by="ci-bot",
        status=status,
        description=description,
        timestamp=datetime.utcnow() - timedelta(minutes=minutes_ago),
    )
    db.add(deployment)
    db.commit()


def _create_and_analyze(db: Session, title: str, description: str, affected_service: str) -> Dict[str, Any]:
    incident = incident_service.create_incident(
        db,
        IncidentCreate(
            title=title,
            description=description,
            severity="LOW",
            status="OPEN",
            affected_service=affected_service,
        ),
    )
    result = analysis_service.run_analysis_for_incident(db, incident)
    return {
        "incident": incident_service.serialize_incident(incident),
        "analysis": result,
    }


def simulate_normal(db: Session, service_name: str = "Payment Service") -> Dict[str, Any]:
    """Generate healthy baseline metrics with no incident."""
    _add_metric_series(
        db, service_name,
        base={"cpu_usage": 30, "memory_usage": 40, "disk_usage": 35, "network_usage": 20, "api_latency": 80, "error_rate": 0.5, "db_connections": 20},
        steps=15,
        drift={"cpu_usage": 0, "memory_usage": 0, "disk_usage": 0, "network_usage": 0, "api_latency": 0, "error_rate": 0, "db_connections": 0},
        start_minutes_ago=15,
    )
    _add_log(db, service_name, "INFO", "Health check passed", 1)
    return {"message": "Normal system baseline generated.", "service": service_name}


def simulate_database_failure(db: Session, service_name: str = "Payment Service") -> Dict[str, Any]:
    """Simulate a database connection pool exhaustion incident."""
    _add_deployment(db, service_name, version="v2.4.1", minutes_ago=10, description="Routine dependency update")
    _add_metric_series(
        db, service_name,
        base={"cpu_usage": 35, "memory_usage": 45, "disk_usage": 40, "network_usage": 25, "api_latency": 90, "error_rate": 0.5, "db_connections": 25},
        steps=10,
        drift={"cpu_usage": 1.5, "memory_usage": 1, "disk_usage": 0.2, "network_usage": 1, "api_latency": 45, "error_rate": 2.2, "db_connections": 7},
        start_minutes_ago=9,
    )
    _add_log(db, service_name, "WARNING", "Database connection pool utilization above 70%", 6, source="database")
    _add_log(db, service_name, "ERROR", "Database connection timeout after 30000ms", 4, error_code="DB_TIMEOUT", source="database", trace_id="trc-9931")
    _add_log(db, service_name, "ERROR", "Database connection timeout: pool exhausted", 3, error_code="DB_TIMEOUT", source="database", trace_id="trc-9932")
    _add_log(db, service_name, "ERROR", "Payment API request failed: HTTP 500 Internal Server Error", 2, error_code="HTTP_500", trace_id="trc-9933")
    _add_log(db, service_name, "CRITICAL", "Multiple payment transactions failing due to database timeout", 1, error_code="DB_TIMEOUT")
    return _create_and_analyze(
        db,
        title="Payment Service Failure",
        description="Elevated errors and latency detected on the payment service.",
        affected_service=service_name,
    )


def simulate_memory_overload(db: Session, service_name: str = "Order Service") -> Dict[str, Any]:
    """Simulate a memory leak / overload incident."""
    _add_deployment(db, service_name, version="v3.1.0", minutes_ago=25, description="New order-batching feature")
    _add_metric_series(
        db, service_name,
        base={"cpu_usage": 40, "memory_usage": 55, "disk_usage": 30, "network_usage": 20, "api_latency": 100, "error_rate": 0.5, "db_connections": 20},
        steps=12,
        drift={"cpu_usage": 1, "memory_usage": 3.2, "disk_usage": 0.1, "network_usage": 0.5, "api_latency": 12, "error_rate": 0.8, "db_connections": 1},
        start_minutes_ago=11,
    )
    _add_log(db, service_name, "WARNING", "Memory usage exceeds 85% threshold", 6, source="application")
    _add_log(db, service_name, "ERROR", "OutOfMemoryError: Java heap space", 4, error_code="OOM", trace_id="trc-4471")
    _add_log(db, service_name, "ERROR", "Possible memory leak detected in order batching module", 2, error_code="OOM")
    return _create_and_analyze(
        db,
        title="Order Service Memory Overload",
        description="Memory usage climbing steadily on the order service.",
        affected_service=service_name,
    )


def simulate_bad_deployment(db: Session, service_name: str = "User Service") -> Dict[str, Any]:
    """Simulate a bad deployment causing elevated error rates."""
    _add_deployment(db, service_name, version="v4.0.0", minutes_ago=8, description="Refactored authentication middleware")
    _add_metric_series(
        db, service_name,
        base={"cpu_usage": 35, "memory_usage": 45, "disk_usage": 30, "network_usage": 25, "api_latency": 95, "error_rate": 1, "db_connections": 22},
        steps=10,
        drift={"cpu_usage": 0.5, "memory_usage": 0.5, "disk_usage": 0.1, "network_usage": 0.5, "api_latency": 20, "error_rate": 4.5, "db_connections": 1},
        start_minutes_ago=7,
    )
    _add_log(db, service_name, "ERROR", "Unhandled exception in AuthMiddleware.validate()", 5, error_code="APP_ERROR", trace_id="trc-2201")
    _add_log(db, service_name, "ERROR", "HTTP 500: authentication middleware raised exception", 4, error_code="HTTP_500", trace_id="trc-2202")
    _add_log(db, service_name, "ERROR", "Increased 5xx responses observed since latest deployment", 2, error_code="HTTP_500")
    return _create_and_analyze(
        db,
        title="User Service Elevated Errors After Deployment",
        description="Error rate increased sharply following the latest release.",
        affected_service=service_name,
    )


def simulate_network_failure(db: Session, service_name: str = "API Gateway") -> Dict[str, Any]:
    """Simulate a network connectivity failure affecting multiple services."""
    _add_metric_series(
        db, service_name,
        base={"cpu_usage": 30, "memory_usage": 40, "disk_usage": 30, "network_usage": 30, "api_latency": 100, "error_rate": 1, "db_connections": 20},
        steps=10,
        drift={"cpu_usage": 0.3, "memory_usage": 0.3, "disk_usage": 0, "network_usage": 6, "api_latency": 30, "error_rate": 3, "db_connections": 0.5},
        start_minutes_ago=9,
    )
    _add_log(db, service_name, "WARNING", "Network usage spike detected between availability zones", 6, source="network")
    _add_log(db, service_name, "ERROR", "Connection refused: unable to reach downstream service", 4, error_code="NET_CONN_REFUSED", trace_id="trc-7781")
    _add_log(db, service_name, "ERROR", "DNS resolution failure for internal service endpoint", 3, error_code="DNS_FAIL")
    _add_log(db, service_name, "ERROR", "Multiple services reporting network unreachable errors", 1, error_code="NET_UNREACHABLE")
    return _create_and_analyze(
        db,
        title="API Gateway Network Connectivity Failure",
        description="Multiple downstream services affected by network issues at the gateway.",
        affected_service=service_name,
    )


def simulate_api_timeout(db: Session, service_name: str = "Order Service") -> Dict[str, Any]:
    """Simulate cascading API timeouts."""
    _add_metric_series(
        db, service_name,
        base={"cpu_usage": 35, "memory_usage": 45, "disk_usage": 30, "network_usage": 25, "api_latency": 120, "error_rate": 1, "db_connections": 22},
        steps=10,
        drift={"cpu_usage": 0.8, "memory_usage": 0.6, "disk_usage": 0.1, "network_usage": 1, "api_latency": 60, "error_rate": 3.5, "db_connections": 1.5},
        start_minutes_ago=9,
    )
    _add_log(db, service_name, "WARNING", "API response times trending upward", 6)
    _add_log(db, service_name, "ERROR", "Request timeout after 30000ms calling downstream inventory service", 4, error_code="API_TIMEOUT", trace_id="trc-5541")
    _add_log(db, service_name, "ERROR", "Gateway timeout: HTTP 504", 2, error_code="HTTP_504", trace_id="trc-5542")
    return _create_and_analyze(
        db,
        title="Order Service API Timeout Incident",
        description="Cascading timeouts observed calling downstream services.",
        affected_service=service_name,
    )
