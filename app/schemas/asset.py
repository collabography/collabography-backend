from pydantic import BaseModel, Field


class AssetPresignRequest(BaseModel):
    """자산 presigned GET URL 요청"""

    object_key: str = Field(..., min_length=1)


class AssetPresignResponse(BaseModel):
    """자산 presigned GET URL 응답"""

    url: str
    expires_in: int


class AssetPresignBatchRequest(BaseModel):
    """자산 presigned GET URL 일괄 요청"""

    object_keys: list[str] = Field(..., min_items=1, max_items=100)


class AssetPresignBatchResponse(BaseModel):
    """자산 presigned GET URL 일괄 응답"""

    urls: dict[str, str]  # object_key -> presigned_url
    expires_in: int

