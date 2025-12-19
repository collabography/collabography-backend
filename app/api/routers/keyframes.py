from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.errors import ErrorResponse
from app.schemas.keyframe import KeyframeUpsert, KeyframeResponse
from app.services.keyframes_service import KeyframesService

router = APIRouter(prefix="/tracks/{track_id}/position-keyframes", tags=["keyframes"])


@router.put(
    "",
    response_model=list[KeyframeResponse],
    status_code=200,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def upsert_keyframes(
    track_id: int,
    data: KeyframeUpsert,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[KeyframeResponse]:
    """키프레임 전체 교체 (upsert)"""
    return await KeyframesService.upsert_keyframes(db, track_id, data)


@router.get(
    "",
    response_model=list[KeyframeResponse],
    responses={404: {"model": ErrorResponse}},
)
async def get_keyframes(
    track_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[KeyframeResponse]:
    """키프레임 목록 조회"""
    return await KeyframesService.get_keyframes(db, track_id)

