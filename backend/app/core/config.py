import os
from pathlib import Path
from typing import Set, Dict, List

# Core application settings
APP_TITLE: str = "HireLens API"
APP_VERSION: str = "1.0.0"
APP_DESCRIPTION: str = "AI-Powered Resume Analyzer & Job Matcher - Phase 3 Backend"

# Security & Upload Constants
MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".docx"}

ALLOWED_MIME_TYPES: Set[str] = {
    "application/pdf",
    "application/x-pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}

# Magic byte signatures for safe file identification
MAGIC_BYTES: Dict[str, List[bytes]] = {
    ".pdf": [b"%PDF-"],
    ".docx": [b"PK\x03\x04"],
}

# CORS settings for development & environment configuration
raw_cors_origins: str = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8001,http://127.0.0.1:8001",
)
CORS_ORIGINS: List[str] = [origin.strip() for origin in raw_cors_origins.split(",") if origin.strip()]

# Base directories
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR: Path = BASE_DIR / "uploads"

# Environment & Server Settings
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
PORT: int = int(os.getenv("PORT", "8001"))
DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes") if ENVIRONMENT.lower() != "production" else False

# Database Settings
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hirelens.db")

# JWT Settings
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "hirelens-dev-secret-key-do-not-use-in-production-123456789")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))


def validate_production_config() -> None:
    """
    Validate that critical security settings are properly set when ENVIRONMENT=production.
    Does NOT affect development or test environments.
    """
    if ENVIRONMENT.lower() == "production":
        insecure_keys = {
            "hirelens-dev-secret-key-do-not-use-in-production-123456789",
            "change-this-to-a-secure-random-secret-key-in-production",
            "",
        }
        if not JWT_SECRET_KEY or JWT_SECRET_KEY.strip() in insecure_keys:
            raise RuntimeError(
                "Production configuration error: A secure, non-default JWT_SECRET_KEY must be provided."
            )
        if "*" in CORS_ORIGINS:
            raise RuntimeError(
                "Production configuration error: Wildcard CORS origins ('*') are prohibited in production."
            )
