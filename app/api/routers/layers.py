from typing import Annotated
from decimal import Decimal

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.errors import ErrorResponse
from app.schemas.layer import LayerUploadResponse, LayerUpdate, LayerResponse
from app.services.layers_service import LayersService

router = APIRouter(prefix="/tracks/{track_id}/layers", tags=["layers"])


@router.post(
    "/upload",
    response_model=LayerUploadResponse,
    status_code=201,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def upload_layer(
    track_id: int,
    file: Annotated[UploadFile, File(...)],
    start_sec: Annotated[Decimal, Form(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
    priority: Annotated[int, Form()] = 0,
    label: Annotated[str | None, Form()] = None,
) -> LayerUploadResponse:
    """레이어 파일 업로드, 프로젝트 연결, 워커 enqueue
    
    서버에서 비디오 파일을 분석하여 end_sec을 자동으로 계산합니다.
    """
    return await LayersService.upload_layer(
        db=db,
        track_id=track_id,
        file=file,
        start_sec=start_sec,
        priority=priority,
        label=label,
    )


@router.get(
    "/{layer_id}",
    response_model=LayerResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_layer(
    track_id: int,
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
    track_id: int,
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
    track_id: int,
    layer_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """레이어 삭제"""
    await LayersService.delete_layer(db, layer_id)
