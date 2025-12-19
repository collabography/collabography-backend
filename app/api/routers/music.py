from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.errors import ErrorResponse
from app.schemas.music import MusicUploadResponse
from app.services.music_service import MusicService
from decimal import Decimal

router = APIRouter(prefix="/projects/{project_id}/music", tags=["music"])


@router.post(
    "/upload",
    response_model=MusicUploadResponse,
    status_code=201,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def upload_music(
    project_id: int,
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
    duration_sec: Annotated[Decimal | None, Form()] = None,
    bpm: Annotated[Decimal | None, Form()] = None,
) -> MusicUploadResponse:
    """음악 파일 업로드 및 프로젝트에 연결"""
    object_key, duration, bpm_value = await MusicService.upload_music(
        db=db,
        project_id=project_id,
        file=file,
        duration_sec=duration_sec,
        bpm=bpm,
    )

    return MusicUploadResponse(
        object_key=object_key,
        duration_sec=duration,
        bpm=bpm_value,
    )
