import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import (
    APP_TITLE,
    APP_VERSION,
    APP_DESCRIPTION,
    CORS_ORIGINS,
    ENVIRONMENT,
    DEBUG,
    PORT,
    validate_production_config,
)
from app.core.exceptions import FileValidationError, FileExtractionError
from app.routers import health, resumes, analysis, auth

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hirelens")

# Validate production security configuration
validate_production_config()

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs" if ENVIRONMENT.lower() != "production" else None,
    redoc_url="/redoc" if ENVIRONMENT.lower() != "production" else None,
    debug=DEBUG,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(FileValidationError)
async def file_validation_exception_handler(request: Request, exc: FileValidationError):
    logger.warning(f"File validation error on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.message,
            "error_type": "FILE_VALIDATION_ERROR",
        },
    )


@app.exception_handler(FileExtractionError)
async def file_extraction_exception_handler(request: Request, exc: FileExtractionError):
    logger.warning(f"File extraction error on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.message,
            "error_type": "FILE_EXTRACTION_ERROR",
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred while processing the request.",
            "error_type": "INTERNAL_SERVER_ERROR",
        },
    )


# Include Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(analysis.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
