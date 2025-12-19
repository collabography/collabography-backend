
import logging

from fastapi import APIRouter, HTTPException, status

from app.db.health import check_db
from app.storage.health import check_minio

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/health/db")
async def health_db() -> dict:
    try:
        await check_db()
    except Exception as exc:
        logger.error("DB health check failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    return {"status": "ok", "db": "ok"}


@router.get("/health/minio")
async def health_minio() -> dict:
    try:
        check_minio()
    except Exception as exc:
        logger.error("MinIO health check failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="minio unavailable",
        ) from exc
    return {"status": "ok", "minio": "ok"}
