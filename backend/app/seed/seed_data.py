"""Generates realistic demo data on first application startup.

Populates services, historical metrics, logs, deployments, and a handful
of already-resolved historical incidents so the dashboard is not empty
the first time the app is opened.
"""
import random
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.service import Service
from app.models.log import Log
from app.models.metric import Metric
from app.models.deployment import Deployment
from app.models.incident import Incident
from app.models.user import User
from app.core.security import hash_password

SERVICES = [
    {"name": "Authentication Service", "service_type": "application", "status": "HEALTHY", "health_score": 98, "cpu_usage": 22, "memory_usage": 38, "dependency_count": 2},
    {"name": "User Service", "service_type": "application", "status": "HEALTHY", "health_score": 97, "cpu_usage": 28, "memory_usage": 42, "dependency_count": 3},
    {"name": "Payment Service", "service_type": "application", "status": "HEALTHY", "health_score": 95, "cpu_usage": 30, "memory_usage": 45, "dependency_count": 4},
    {"name": "Order Service", "service_type": "application", "status": "HEALTHY", "health_score": 96, "cpu_usage": 33, "memory_usage": 47, "dependency_count": 3},
    {"name": "Notification Service", "service_type": "application", "status": "HEALTHY", "health_score": 99, "cpu_usage": 18, "memory_usage": 30, "dependency_count": 2},
    {"name": "API Gateway", "service_type": "infrastructure", "status": "HEALTHY", "health_score": 98, "cpu_usage": 25, "memory_usage": 35, "dependency_count": 6},
    {"name": "Database", "service_type": "infrastructure", "status": "HEALTHY", "health_score": 97, "cpu_usage": 40, "memory_usage": 55, "dependency_count": 0},
    {"name": "Redis Cache", "service_type": "infrastructure", "status": "HEALTHY", "health_score": 99, "cpu_usage": 15, "memory_usage": 25, "dependency_count": 0},
]

LOG_MESSAGES_NORMAL = [
    ("INFO", "Request processed successfully"),
    ("INFO", "Health check passed"),
    ("INFO", "Cache hit for key lookup"),
    ("DEBUG", "Scheduled job completed"),
    ("WARNING", "Response time slightly above baseline"),
]

LOG_MESSAGES_ABNORMAL = [
    ("ERROR", "Database connection timeout after 30000ms", "DB_TIMEOUT"),
    ("ERROR", "HTTP 500 Internal Server Error", "HTTP_500"),
    ("ERROR", "Request timeout calling downstream service", "API_TIMEOUT"),
    ("CRITICAL", "Service unavailable: circuit breaker open", "SERVICE_DOWN"),
    ("ERROR", "OutOfMemoryError: Java heap space", "OOM"),
]


def _random_timestamp(hours_back: int) -> datetime:
    return datetime.utcnow() - timedelta(
        hours=random.uniform(0, hours_back), minutes=random.uniform(0, 59)
    )


def seed_if_empty(db: Session) -> None:
    """Populate the database with demo data only if it is currently empty."""
    if db.query(Service).count() > 0:
        return

    # Demo admin user
    admin = User(
        username="admin",
        email="admin@cognitiveops.local",
        password_hash=hash_password("admin123"),
        role="admin",
    )
    db.add(admin)

    services = []
    for s in SERVICES:
        service = Service(**s)
        db.add(service)
        services.append(service)
    db.commit()

    service_names = [s["name"] for s in SERVICES]

    # 100+ metrics across services and time
    for _ in range(120):
        service_name = random.choice(service_names)
        ts = _random_timestamp(72)
        db.add(Metric(
            service_name=service_name,
            timestamp=ts,
            cpu_usage=random.uniform(15, 55),
            memory_usage=random.uniform(25, 60),
            disk_usage=random.uniform(20, 50),
            network_usage=random.uniform(10, 40),
            api_latency=random.uniform(50, 180),
            error_rate=random.uniform(0, 2),
            db_connections=random.uniform(10, 35),
        ))
    db.commit()

    # 100+ logs, mostly normal with a handful of abnormal ones sprinkled in
    for _ in range(110):
        service_name = random.choice(service_names)
        ts = _random_timestamp(72)
        level, message = random.choice(LOG_MESSAGES_NORMAL)
        db.add(Log(
            service_name=service_name,
            timestamp=ts,
            level=level,
            message=message,
            source="application",
        ))
    for _ in range(15):
        service_name = random.choice(service_names)
        ts = _random_timestamp(72)
        level, message, error_code = random.choice(LOG_MESSAGES_ABNORMAL)
        db.add(Log(
            service_name=service_name,
            timestamp=ts,
            level=level,
            message=message,
            source="application",
            error_code=error_code,
            trace_id=f"trc-{random.randint(1000, 9999)}",
        ))
    db.commit()

    # 10 deployments
    versions = ["v1.0.0", "v1.1.0", "v1.2.0", "v2.0.0", "v2.1.0", "v2.2.0", "v2.3.0", "v2.4.0", "v3.0.0", "v3.1.0"]
    for i, version in enumerate(versions):
        service_name = random.choice(service_names)
        db.add(Deployment(
            service_name=service_name,
            version=version,
            environment="production",
            deployed_by="ci-bot",
            status="SUCCESS",
            description=f"Automated deployment of {version}",
            timestamp=datetime.utcnow() - timedelta(hours=(len(versions) - i) * 6),
        ))
    db.commit()

    # 5 historical (resolved) incidents
    historical_incidents = [
        ("Database Connection Pool Exhaustion", "Payment Service", "DATABASE_CONNECTION_EXHAUSTION", 91.0, "CRITICAL", 82.0),
        ("Memory Leak in Order Batching", "Order Service", "MEMORY_OVERLOAD", 87.0, "HIGH", 68.0),
        ("Elevated Errors After Deployment", "User Service", "BAD_DEPLOYMENT", 84.0, "HIGH", 61.0),
        ("API Gateway Network Blip", "API Gateway", "NETWORK_FAILURE", 76.0, "MEDIUM", 45.0),
        ("Disk Space Warning on Database Host", "Database", "DISK_SPACE_EXHAUSTION", 72.0, "MEDIUM", 40.0),
    ]
    for title, service_name, root_cause, confidence, severity, impact in historical_incidents:
        created = datetime.utcnow() - timedelta(days=random.randint(2, 14))
        db.add(Incident(
            title=title,
            description=f"Historical incident affecting {service_name}.",
            severity=severity,
            status="RESOLVED",
            affected_service=service_name,
            probable_root_cause=root_cause,
            confidence_score=confidence,
            impact_score=impact,
            evidence=json.dumps([f"Elevated metrics observed on {service_name}", "Anomaly detected by monitoring"]),
            recommendations=json.dumps(["Reviewed and mitigated by on-call engineer"]),
            timeline=json.dumps([]),
            contributing_factors=json.dumps({root_cause: confidence / 100}),
            created_at=created,
            resolved_at=created + timedelta(hours=random.randint(1, 6)),
        ))
    db.commit()
