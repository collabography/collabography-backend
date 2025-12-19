
from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """공통 에러 응답 포맷"""

    error: str
    detail: str | None = None
    code: str | None = None


class NotFoundError(HTTPException):
    """리소스를 찾을 수 없을 때"""

    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id {identifier} not found",
        )


class ValidationError(HTTPException):
    """검증 오류"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class ConflictError(HTTPException):
    """충돌 오류 (예: 중복된 리소스)"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

