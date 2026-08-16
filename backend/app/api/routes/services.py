"""Service resource endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceOut, ServiceCreate, ServiceUpdate

router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("", response_model=List[ServiceOut], summary="List all services")
def list_services(db: Session = Depends(get_db)):
    return db.query(Service).order_by(Service.name.asc()).all()


@router.get("/{service_id}", response_model=ServiceOut, summary="Get a service by ID")
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("", response_model=ServiceOut, status_code=201, summary="Create a new service")
def create_service(service_in: ServiceCreate, db: Session = Depends(get_db)):
    existing = db.query(Service).filter(Service.name == service_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="A service with this name already exists")
    service = Service(**service_in.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.put("/{service_id}", response_model=ServiceOut, summary="Update a service")
def update_service(service_id: int, service_in: ServiceUpdate, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    for field, value in service_in.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service
