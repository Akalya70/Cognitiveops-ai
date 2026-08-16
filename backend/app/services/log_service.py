"""Business logic for Log resources."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.log import Log
from app.schemas.log import LogCreate


def create_log(db: Session, log_in: LogCreate) -> Log:
    log = Log(
        service_name=log_in.service_name,
        level=log_in.level,
        message=log_in.message,
        source=log_in.source,
        error_code=log_in.error_code,
        trace_id=log_in.trace_id,
        timestamp=log_in.timestamp or datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_log(db: Session, log_id: int) -> Optional[Log]:
    return db.query(Log).filter(Log.id == log_id).first()


def list_logs(
    db: Session,
    service_name: Optional[str] = None,
    level: Optional[str] = None,
    error_code: Optional[str] = None,
    date: Optional[str] = None,
    skip: int = 0,
    limit: int = 200,
) -> List[Log]:
    query = db.query(Log)
    if service_name:
        query = query.filter(Log.service_name == service_name)
    if level:
        query = query.filter(Log.level == level)
    if error_code:
        query = query.filter(Log.error_code == error_code)
    if date:
        try:
            day = datetime.fromisoformat(date).date()
            query = query.filter(Log.timestamp >= datetime(day.year, day.month, day.day))
        except ValueError:
            pass
    return query.order_by(Log.timestamp.desc()).offset(skip).limit(limit).all()


def get_logs_for_service(db: Session, service_name: str, since: datetime, limit: int = 500) -> List[Log]:
    return (
        db.query(Log)
        .filter(Log.service_name == service_name, Log.timestamp >= since)
        .order_by(Log.timestamp.asc())
        .limit(limit)
        .all()
    )
