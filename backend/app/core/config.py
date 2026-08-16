"""Application configuration loaded from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central application settings."""

    APP_NAME: str = os.getenv("APP_NAME", "CognitiveOps AI")
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cognitiveops.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Root cause categories used throughout the AI engine
    ROOT_CAUSES: list = [
        "DATABASE_CONNECTION_EXHAUSTION",
        "MEMORY_OVERLOAD",
        "HIGH_CPU_USAGE",
        "API_TIMEOUT",
        "NETWORK_FAILURE",
        "BAD_DEPLOYMENT",
        "DEPENDENCY_FAILURE",
        "DISK_SPACE_EXHAUSTION",
        "UNKNOWN",
    ]

    INCIDENT_STATUSES: list = ["OPEN", "INVESTIGATING", "MITIGATED", "RESOLVED"]
    SEVERITY_LEVELS: list = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


settings = Settings()
