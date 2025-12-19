from decimal import Decimal

from pydantic import BaseModel, Field


class LayerUploadRequest(BaseModel):
    """레이어 업로드 요청 (파일 + 메타데이터)"""

    # 레이어 메타
    start_sec: Decimal = Field(..., ge=0, description="시작 시간 (초)")
    end_sec: Decimal = Field(..., gt=0, description="종료 시간 (초)")
    priority: int = Field(default=0, description="우선순위 (z-index)")
    label: str | None = Field(None, max_length=255, description="레이어 라벨")


class LayerUploadResponse(BaseModel):
    """레이어 업로드 응답"""

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
