from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.errors import ErrorResponse
from app.schemas.common import CursorResponse
from app.schemas.project import ProjectCreate, ProjectResponse, EditStateResponse
from app.services.projects_service import ProjectsService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=201,
    responses={422: {"model": ErrorResponse}},
)
async def create_project(
    data: ProjectCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectResponse:
    """프로젝트 생성"""
    return await ProjectsService.create_project(db, data)


@router.get(
    "",
    response_model=CursorResponse[ProjectResponse],
    responses={422: {"model": ErrorResponse}},
)
async def list_projects(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[str | None, Query()] = None,
) -> CursorResponse[ProjectResponse]:
    """프로젝트 목록 조회"""
    projects = await ProjectsService.list_projects(db, limit=limit, cursor=cursor)

    next_cursor = None
    has_more = False
    if len(projects) == limit:
        next_cursor = str(projects[-1].id)
        has_more = True

    return CursorResponse(
        items=projects,
        next_cursor=next_cursor,
        has_more=has_more,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_project(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectResponse:
    """프로젝트 조회"""
    return await ProjectsService.get_project(db, project_id)


@router.get(
    "/{project_id}/edit-state",
    response_model=EditStateResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_edit_state(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EditStateResponse:
    """프로젝트 edit-state 조회 (프론트 렌더링용 전체 상태)"""
    return await ProjectsService.get_edit_state(db, project_id)

