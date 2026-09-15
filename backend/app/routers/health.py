from fastapi import APIRouter
from app.core.config import APP_TITLE, APP_VERSION
from app.schemas.resume import HealthCheckResponse

router = APIRouter(tags=["Health"])


@router.get("/", response_model=dict, summary="Root health check endpoint")
async def root_health_check():
    """Root status endpoint returning basic application metadata."""
    return {
        "status": "ok",
        "message": f"Welcome to {APP_TITLE} (Phase 1 Foundation)",
        "version": APP_VERSION,
    }


@router.get(
    "/api/v1/health",
    response_model=HealthCheckResponse,
    summary="V1 Health check status endpoint",
)
async def api_v1_health_check():
    """Detailed health check endpoint for monitoring API status."""
    return HealthCheckResponse(
        status="ok",
        version=APP_VERSION,
        app_name=APP_TITLE,
    )
