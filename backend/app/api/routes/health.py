"""Health check endpoint."""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("", summary="Health check", description="Returns application status and version.")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
