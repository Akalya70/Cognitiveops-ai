"""Pydantic schemas for Metric resources."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MetricBase(BaseModel):
    service_name: str
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_usage: float = 0.0
    api_latency: float = 0.0
    error_rate: float = 0.0
    db_connections: float = 0.0


class MetricCreate(MetricBase):
    timestamp: Optional[datetime] = None


class MetricOut(MetricBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
