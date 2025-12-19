from decimal import Decimal

from pydantic import BaseModel, Field


class MusicUploadRequest(BaseModel):
    """음악 업로드 요청 (파일 + 메타데이터)"""

    duration_sec: Decimal | None = Field(None, description="음악 길이 (초)")
    bpm: Decimal | None = Field(None, description="BPM")


class MusicUploadResponse(BaseModel):
    """음악 업로드 응답"""

    object_key: str
    duration_sec: Decimal | None = None
    bpm: Decimal | None = None
