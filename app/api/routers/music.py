from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.errors import ErrorResponse
from app.schemas.music import MusicUploadInit, MusicUploadInitResponse, MusicCommit
from app.services.music_service import MusicService
from datetime import timedelta

router = APIRouter(prefix="/projects/{project_id}/music", tags=["music"])


@router.post(
    "/upload-init",
    response_model=MusicUploadInitResponse,
    status_code=201,
    responses={422: {"model": ErrorResponse}},
)
async def init_music_upload(
    project_id: int,
    data: MusicUploadInit,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MusicUploadInitResponse:
    """음악 업로드 presigned URL 발급"""
    url, object_key = await MusicService.get_upload_url(
        project_id=project_id,
        filename=data.filename,
        content_type=data.content_type,
    )

    return MusicUploadInitResponse(
        upload_url=url,
        object_key=object_key,
        expires_in=int(timedelta(hours=1).total_seconds()),
    )


@router.post(
    "/commit",
    response_model=dict,
    status_code=200,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def commit_music(
    project_id: int,
    data: MusicCommit,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """음악 업로드 완료 후 프로젝트에 연결"""
    await MusicService.commit_music(db, project_id, data)
    return {"status": "ok"}

