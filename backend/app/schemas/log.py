"""Pydantic schemas for Log resources."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class LogBase(BaseModel):
    service_name: str
    level: str = "INFO"
    message: str
    source: Optional[str] = "application"
    error_code: Optional[str] = None
    trace_id: Optional[str] = None


class LogCreate(LogBase):
    timestamp: Optional[datetime] = None


class LogOut(LogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
