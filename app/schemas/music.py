from decimal import Decimal

from pydantic import BaseModel, Field


class MusicUploadInit(BaseModel):
    """음악 업로드 presigned URL 요청"""

    filename: str = Field(..., min_length=1)
    content_type: str = Field(default="audio/mpeg")


class MusicUploadInitResponse(BaseModel):
    """음악 업로드 presigned URL 응답"""

    upload_url: str
    object_key: str
    expires_in: int


class MusicCommit(BaseModel):
    """음악 업로드 완료 후 프로젝트에 연결"""

    object_key: str
    duration_sec: Decimal | None = None
    bpm: Decimal | None = None

