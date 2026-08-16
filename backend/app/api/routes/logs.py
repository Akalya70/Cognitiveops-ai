"""Log resource endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.log import LogOut, LogCreate
from app.services import log_service

router = APIRouter(prefix="/api/logs", tags=["Logs"])


@router.get("", response_model=List[LogOut], summary="List logs with optional filters")
def list_logs(
    service: Optional[str] = Query(default=None),
    level: Optional[str] = Query(default=None),
    date: Optional[str] = Query(default=None),
    error_code: Optional[str] = Query(default=None),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    return log_service.list_logs(db, service_name=service, level=level, error_code=error_code, date=date, skip=skip, limit=limit)


@router.post("", response_model=LogOut, status_code=201, summary="Create a log entry")
def create_log(log_in: LogCreate, db: Session = Depends(get_db)):
    return log_service.create_log(db, log_in)


@router.get("/{log_id}", response_model=LogOut, summary="Get a log entry by ID")
def get_log(log_id: int, db: Session = Depends(get_db)):
    log = log_service.get_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
