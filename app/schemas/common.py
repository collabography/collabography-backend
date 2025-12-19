from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """공통 에러 응답"""

    error: str
    detail: str | None = None
    code: str | None = None


class CursorResponse(BaseModel, Generic[T]):
    """커서 기반 페이지네이션 응답"""

    items: list[T]
    next_cursor: str | None = None
    has_more: bool = False

