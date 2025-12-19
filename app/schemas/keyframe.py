from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import InterpType


class KeyframeResponse(BaseModel):
    """키프레임 응답"""

    id: int
    track_id: int
    time_sec: Decimal
    x: Decimal
    y: Decimal
    interp: InterpType

    class Config:
        from_attributes = True


class KeyframeUpsert(BaseModel):
    """키프레임 전체 교체 요청"""

    keyframes: list["KeyframeItem"]


class KeyframeItem(BaseModel):
    """키프레임 항목"""

    time_sec: Decimal = Field(..., ge=0)
    x: Decimal
    y: Decimal
    interp: InterpType = Field(default=InterpType.LINEAR)

