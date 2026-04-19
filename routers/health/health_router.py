"""
Health and home router — checks real connectivity to external dependencies.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import asyncio

from config.logger_config import get_logger
from config.settings import FILE_UPLOAD_API_URL

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


class DependencyStatus(BaseModel):
    name: str
    status: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    message: str
    dependencies: Optional[list[DependencyStatus]] = None


@router.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - basic liveness check."""
    return HealthResponse(status="healthy", message="BCT Database API is running")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Deep health check — verifies connectivity to PostgreSQL and external APIs.
    Returns 503 if any critical dependency is unreachable.
    """
    from fastapi.responses import JSONResponse
    from sqlalchemy import text
    from database.dbConnection.postgres_connection import get_postgres_manager

    deps: list[DependencyStatus] = []
    all_ok = True

    # --- PostgreSQL ---
    try:
        manager = get_postgres_manager()
        engine = manager.get_engine()
        async with engine.connect() as conn:
            await asyncio.wait_for(conn.execute(text("SELECT 1")), timeout=5.0)
        deps.append(DependencyStatus(name="postgresql", status="ok"))
        logger.info("PostgreSQL health check passed")
    except Exception as e:
        all_ok = False
        deps.append(DependencyStatus(name="postgresql", status="error", error=str(e)))
        logger.error(f"PostgreSQL health check failed: {e}")

    # --- File Upload API ---
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await asyncio.wait_for(
                client.head(FILE_UPLOAD_API_URL),
                timeout=5.0
            )
            if response.status_code < 500:
                deps.append(DependencyStatus(name="file_upload_api", status="ok"))
                logger.info("File Upload API health check passed")
            else:
                raise Exception(f"API returned status {response.status_code}")
    except Exception as e:
        all_ok = False
        deps.append(DependencyStatus(name="file_upload_api", status="error", error=str(e)))
        logger.error(f"File Upload API health check failed: {e}")

    status = "healthy" if all_ok else "degraded"
    message = "All dependencies operational" if all_ok else "One or more dependencies unavailable"
    response = HealthResponse(status=status, message=message, dependencies=deps)

    if not all_ok:
        return JSONResponse(status_code=503, content=response.model_dump())

    return response
