"""Pydantic schemas for Incident resources."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "LOW"
    status: str = "OPEN"
    affected_service: str
    probable_root_cause: Optional[str] = None
    confidence_score: Optional[float] = 0.0
    impact_score: Optional[float] = 0.0


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    affected_service: Optional[str] = None
    probable_root_cause: Optional[str] = None
    confidence_score: Optional[float] = None
    impact_score: Optional[float] = None


class IncidentOut(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    evidence: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    contributing_factors: Optional[Dict[str, float]] = None


class IncidentAnalysisResult(BaseModel):
    incident_id: int
    root_cause: str
    confidence: float
    severity: str
    impact_score: float
    evidence: List[str]
    recommendations: List[str]
    timeline: List[Dict[str, Any]]
    contributing_factors: Dict[str, float]
