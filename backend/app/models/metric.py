"""Metric model storing point-in-time telemetry for a service."""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    service_name = Column(String(120), index=True, nullable=False)
    cpu_usage = Column(Float, nullable=False, default=0.0)
    memory_usage = Column(Float, nullable=False, default=0.0)
    disk_usage = Column(Float, nullable=False, default=0.0)
    network_usage = Column(Float, nullable=False, default=0.0)
    api_latency = Column(Float, nullable=False, default=0.0)
    error_rate = Column(Float, nullable=False, default=0.0)
    db_connections = Column(Float, nullable=False, default=0.0)
