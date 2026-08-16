"""Pydantic schemas for Service resources."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):
    name: str
    service_type: str = "application"
    status: str = "HEALTHY"
    health_score: float = 100.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    dependency_count: int = 0


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    service_type: Optional[str] = None
    status: Optional[str] = None
    health_score: Optional[float] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    dependency_count: Optional[int] = None


class ServiceOut(ServiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
