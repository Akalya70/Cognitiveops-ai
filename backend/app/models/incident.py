"""Incident model representing a detected/declared IT incident."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False, default="LOW")
    status = Column(String(30), nullable=False, default="OPEN")
    affected_service = Column(String(120), nullable=False)
    probable_root_cause = Column(String(60), nullable=True)
    confidence_score = Column(Float, nullable=True, default=0.0)
    impact_score = Column(Float, nullable=True, default=0.0)
    evidence = Column(Text, nullable=True)  # JSON-encoded list of evidence strings
    recommendations = Column(Text, nullable=True)  # JSON-encoded list of recommendation strings
    timeline = Column(Text, nullable=True)  # JSON-encoded list of timeline events
    contributing_factors = Column(Text, nullable=True)  # JSON-encoded dict of root cause scores
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)
