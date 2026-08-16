"""Log model representing an application/infrastructure log entry."""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    service_name = Column(String(120), index=True, nullable=False)
    level = Column(String(20), nullable=False, default="INFO")  # DEBUG/INFO/WARNING/ERROR/CRITICAL
    message = Column(Text, nullable=False)
    source = Column(String(120), nullable=True, default="application")
    error_code = Column(String(40), nullable=True)
    trace_id = Column(String(64), nullable=True, index=True)
