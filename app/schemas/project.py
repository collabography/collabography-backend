from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.schemas.keyframe import KeyframeResponse


class ProjectCreate(BaseModel):
    """프로젝트 생성 요청"""

    title: str = Field(..., min_length=1, max_length=255)


class ProjectUpdate(BaseModel):
    """프로젝트 상태 업데이트 (edit-state 조합용)"""

    pass  # MVP에서는 별도 필드 없음


class ProjectResponse(BaseModel):
    """프로젝트 응답"""

    id: int
    title: str
    music_object_key: str | None = None
    music_duration_sec: Decimal | None = None
    music_bpm: Decimal | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EditStateResponse(BaseModel):
    """프로젝트 edit-state 응답 (프론트 렌더링용 전체 상태)"""

    project: ProjectResponse
    tracks: list["TrackEditState"]


class TrackEditState(BaseModel):
    """트랙별 편집 상태"""

    id: int
    slot: int
    display_name: str | None = None
    layers: list["LayerEditState"]
    keyframes: list["KeyframeResponse"]


class LayerEditState(BaseModel):
    """레이어 편집 상태 (source 포함)"""

    id: int
    skeleton_source_id: int
    start_sec: Decimal
    end_sec: Decimal
    priority: int
    label: str | None = None
    source_status: str  # AssetStatus
    source_object_key: str | None = None
    source_fps: float | None = None
    source_num_frames: int | None = None
    source_num_joints: int | None = None

