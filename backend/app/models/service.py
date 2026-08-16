"""Service model representing a monitored application/infrastructure component."""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, index=True, nullable=False)
    service_type = Column(String(60), nullable=False, default="application")
    status = Column(String(30), nullable=False, default="HEALTHY")
    health_score = Column(Float, nullable=False, default=100.0)
    cpu_usage = Column(Float, nullable=False, default=0.0)
    memory_usage = Column(Float, nullable=False, default=0.0)
    dependency_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
