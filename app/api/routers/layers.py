from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.errors import ErrorResponse
from app.schemas.layer import (
    LayerUploadInit,
    LayerUploadInitResponse,
    LayerCreate,
    LayerUpdate,
    LayerResponse,
)
from app.services.layers_service import LayersService
from datetime import timedelta

router = APIRouter(prefix="/tracks/{track_id}/layers", tags=["layers"])


@router.post(
    "/upload-init",
    response_model=LayerUploadInitResponse,
    status_code=201,
    responses={422: {"model": ErrorResponse}},
)
async def init_layer_upload(
    track_id: int,
    data: LayerUploadInit,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LayerUploadInitResponse:
    """레이어 업로드 presigned URL 발급"""
    url, object_key = await LayersService.get_upload_url(
        track_id=track_id,
        filename=data.filename,
        content_type=data.content_type,
    )

    return LayerUploadInitResponse(
        upload_url=url,
        object_key=object_key,
        expires_in=int(timedelta(hours=1).total_seconds()),
    )


@router.post(
    "",
    response_model=LayerResponse,
    status_code=201,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def create_layer(
    track_id: int,
    data: LayerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LayerResponse:
    """레이어 생성 (VIDEO 또는 JSON 기반)"""
    return await LayersService.create_layer(db, track_id, data)


@router.get(
    "/{layer_id}",
    response_model=LayerResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_layer(
    layer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LayerResponse:
    """레이어 조회 (상태 포함)"""
    return await LayersService.get_layer(db, layer_id)


@router.patch(
    "/{layer_id}",
    response_model=LayerResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def update_layer(
    layer_id: int,
    data: LayerUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LayerResponse:
    """레이어 업데이트"""
    return await LayersService.update_layer(db, layer_id, data)


@router.delete(
    "/{layer_id}",
    status_code=204,
    responses={404: {"model": ErrorResponse}},
)
async def delete_layer(
    layer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """레이어 삭제"""
    await LayersService.delete_layer(db, layer_id)

