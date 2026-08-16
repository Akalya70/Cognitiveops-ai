"""Deployment model representing a release/deployment event."""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(120), index=True, nullable=False)
    version = Column(String(60), nullable=False)
    environment = Column(String(40), nullable=False, default="production")
    deployed_by = Column(String(80), nullable=False, default="ci-bot")
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    status = Column(String(30), nullable=False, default="SUCCESS")  # SUCCESS/FAILED/ROLLED_BACK
    description = Column(Text, nullable=True)
