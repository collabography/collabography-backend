from decimal import Decimal

from pydantic import BaseModel, Field


class LayerUploadInit(BaseModel):
    """레이어 업로드 presigned URL 요청"""

    filename: str = Field(..., min_length=1)
    content_type: str = Field(default="video/mp4")


class LayerUploadInitResponse(BaseModel):
    """레이어 업로드 presigned URL 응답"""

    upload_url: str
    object_key: str
    expires_in: int


class LayerCreate(BaseModel):
    """레이어 생성 요청"""

    # VIDEO 기반
    video_object_key: str | None = None

    # JSON 기반 (직접 스켈레톤 JSON 업로드)
    skeleton_object_key: str | None = None
    skeleton_fps: float | None = None
    skeleton_num_frames: int | None = None
    skeleton_num_joints: int | None = None

    # 레이어 메타
    start_sec: Decimal = Field(..., ge=0)
    end_sec: Decimal = Field(..., gt=0)
    priority: int = Field(default=0)
    label: str | None = Field(None, max_length=255)


class LayerUpdate(BaseModel):
    """레이어 업데이트 요청"""

    start_sec: Decimal | None = Field(None, ge=0)
    end_sec: Decimal | None = Field(None, gt=0)
    priority: int | None = None
    label: str | None = Field(None, max_length=255)


class LayerResponse(BaseModel):
    """레이어 응답 (상태 포함)"""

    id: int
    track_id: int
    skeleton_source_id: int
    start_sec: Decimal
    end_sec: Decimal
    priority: int
    label: str | None = None
    created_at: str  # ISO format

    # Source 정보
    source_status: str  # AssetStatus
    source_object_key: str | None = None
    source_fps: float | None = None
    source_num_frames: int | None = None
    source_num_joints: int | None = None
    source_error_message: str | None = None

    class Config:
        from_attributes = True

