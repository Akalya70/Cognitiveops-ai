"""Pydantic schemas for Deployment resources."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DeploymentBase(BaseModel):
    service_name: str
    version: str
    environment: str = "production"
    deployed_by: str = "ci-bot"
    status: str = "SUCCESS"
    description: Optional[str] = None


class DeploymentCreate(DeploymentBase):
    timestamp: Optional[datetime] = None


class DeploymentOut(DeploymentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
