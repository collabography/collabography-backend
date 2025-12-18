import traceback

from fastapi import APIRouter, HTTPException, status

from app.db.health import check_db

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/health/db")
async def health_db() -> dict:
    try:
        await check_db()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    return {"status": "ok", "db": "ok"}
