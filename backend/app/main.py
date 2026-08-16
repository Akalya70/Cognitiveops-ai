"""FastAPI application factory and startup wiring."""
import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.seed.seed_data import seed_if_empty
from app.api.routes import (
    health,
    incidents,
    logs,
    metrics,
    services,
    deployments,
    dashboard,
    analysis,
    simulation,
    auth,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("cognitiveops")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Context-aware IT root cause analysis and decision assistant.",
    openapi_tags=[
        {"name": "Health", "description": "Service liveness checks."},
        {"name": "Dashboard", "description": "Aggregated system health summary."},
        {"name": "Incidents", "description": "Incident lifecycle and AI analysis."},
        {"name": "Logs", "description": "Application and infrastructure logs."},
        {"name": "Metrics", "description": "Time-series service telemetry."},
        {"name": "Services", "description": "Monitored services and their health."},
        {"name": "Deployments", "description": "Deployment/release events."},
        {"name": "Analysis", "description": "Ad-hoc AI root cause analysis."},
        {"name": "Simulation", "description": "Demo scenario generators."},
        {"name": "Authentication", "description": "Demo login system."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error on %s: %s", request.url, exc.errors())
    return JSONResponse(status_code=422, content={"success": False, "message": "Validation error", "details": exc.errors()})


@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error("Database error on %s: %s", request.url, str(exc))
    return JSONResponse(status_code=500, content={"success": False, "message": "A database error occurred", "details": None})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s: %s\n%s", request.url, str(exc), traceback.format_exc())
    return JSONResponse(status_code=500, content={"success": False, "message": "An unexpected error occurred", "details": None})


app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(incidents.router)
app.include_router(logs.router)
app.include_router(metrics.router)
app.include_router(services.router)
app.include_router(deployments.router)
app.include_router(analysis.router)
app.include_router(simulation.router)
app.include_router(auth.router)


@app.on_event("startup")
def on_startup():
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    init_db()
    db = SessionLocal()
    try:
        seed_if_empty(db)
        logger.info("Seed data check complete.")
    finally:
        db.close()


@app.get("/", tags=["Health"], summary="Root endpoint")
def root():
    return {
        "message": f"{settings.APP_NAME} API is running.",
        "docs": "/docs",
        "health": "/api/health",
    }
