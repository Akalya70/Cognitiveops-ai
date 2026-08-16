"""Deployment resource endpoints."""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentOut, DeploymentCreate

router = APIRouter(prefix="/api/deployments", tags=["Deployments"])


@router.get("", response_model=List[DeploymentOut], summary="List deployments")
def list_deployments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Deployment).order_by(Deployment.timestamp.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=DeploymentOut, status_code=201, summary="Create a deployment record")
def create_deployment(deployment_in: DeploymentCreate, db: Session = Depends(get_db)):
    deployment = Deployment(
        **deployment_in.model_dump(exclude={"timestamp"}),
        timestamp=deployment_in.timestamp or datetime.utcnow(),
    )
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    return deployment


@router.get("/{deployment_id}", response_model=DeploymentOut, summary="Get a deployment by ID")
def get_deployment(deployment_id: int, db: Session = Depends(get_db)):
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment
