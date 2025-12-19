from typing import Annotated

from fastapi import APIRouter

from app.core.errors import ErrorResponse
from app.schemas.asset import (
    AssetPresignRequest,
    AssetPresignResponse,
    AssetPresignBatchRequest,
    AssetPresignBatchResponse,
)
from app.services.assets_service import AssetsService
from datetime import timedelta

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post(
    "/presign",
    response_model=AssetPresignResponse,
    status_code=200,
    responses={422: {"model": ErrorResponse}},
)
async def get_presigned_url(
    data: AssetPresignRequest,
) -> AssetPresignResponse:
    """자산 presigned GET URL 발급"""
    url = AssetsService.get_presigned_url(
        object_key=data.object_key,
        expires_hours=1,
    )

    return AssetPresignResponse(
        url=url,
        expires_in=int(timedelta(hours=1).total_seconds()),
    )


@router.post(
    "/presign/batch",
    response_model=AssetPresignBatchResponse,
    status_code=200,
    responses={422: {"model": ErrorResponse}},
)
async def get_presigned_urls_batch(
    data: AssetPresignBatchRequest,
) -> AssetPresignBatchResponse:
    """자산 presigned GET URL 일괄 발급"""
    urls = AssetsService.get_presigned_urls_batch(
        object_keys=data.object_keys,
        expires_hours=1,
    )

    return AssetPresignBatchResponse(
        urls=urls,
        expires_in=int(timedelta(hours=1).total_seconds()),
    )

