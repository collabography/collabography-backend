from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import NotFoundError
from app.models import Project, Track, SkeletonLayer, SkeletonSource, TrackPositionKeyframe
from app.schemas.project import ProjectCreate, ProjectResponse, EditStateResponse, TrackEditState, LayerEditState
from app.schemas.keyframe import KeyframeResponse


class ProjectsService:
    @staticmethod
    async def create_project(db: AsyncSession, data: ProjectCreate) -> ProjectResponse:
        """프로젝트 생성"""
        project = Project(
            title=data.title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(project)
        await db.flush()

        # 프로젝트 생성 시 3개의 트랙 자동 생성
        for slot in [1, 2, 3]:
            track = Track(
                project_id=project.id,
                slot=slot,
                created_at=datetime.utcnow(),
            )
            db.add(track)

        await db.commit()
        await db.refresh(project)

        return ProjectResponse.model_validate(project)

    @staticmethod
    async def get_project(db: AsyncSession, project_id: int) -> ProjectResponse:
        """프로젝트 조회"""
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise NotFoundError("Project", project_id)

        return ProjectResponse.model_validate(project)

    @staticmethod
    async def list_projects(db: AsyncSession, limit: int = 50, cursor: str | None = None) -> list[ProjectResponse]:
        """프로젝트 목록 조회"""
        query = select(Project).order_by(Project.id.desc()).limit(limit)

        if cursor:
            try:
                cursor_id = int(cursor)
                query = query.where(Project.id < cursor_id)
            except ValueError:
                pass

        result = await db.execute(query)
        projects = result.scalars().all()

        return [ProjectResponse.model_validate(p) for p in projects]

    @staticmethod
    async def get_edit_state(db: AsyncSession, project_id: int) -> EditStateResponse:
        """프로젝트 edit-state 조회 (프론트 렌더링용 전체 상태)"""
        # 프로젝트 조회
        project_result = await db.execute(select(Project).where(Project.id == project_id))
        project = project_result.scalar_one_or_none()

        if not project:
            raise NotFoundError("Project", project_id)

        # 트랙 조회 (레이어, 소스, 키프레임 포함)
        tracks_result = await db.execute(
            select(Track)
            .where(Track.project_id == project_id)
            .options(
                selectinload(Track.layers).selectinload(SkeletonLayer.source),
                selectinload(Track.keyframes),
            )
            .order_by(Track.slot)
        )
        tracks = tracks_result.scalars().all()

        # 트랙별 편집 상태 구성
        track_states = []
        for track in tracks:
            # 레이어 상태 구성
            layers = []
            for layer in track.layers:
                source = layer.source
                layers.append(
                    LayerEditState(
                        id=layer.id,
                        skeleton_source_id=layer.skeleton_source_id,
                        start_sec=layer.start_sec,
                        end_sec=layer.end_sec,
                        priority=layer.priority,
                        label=layer.label,
                        source_status=source.status.value,
                        source_object_key=source.object_key,
                        source_fps=source.fps,
                        source_num_frames=source.num_frames,
                        source_num_joints=source.num_joints,
                    )
                )

            # 키프레임 구성
            keyframes = [KeyframeResponse.model_validate(kf) for kf in sorted(track.keyframes, key=lambda k: k.time_sec)]

            track_states.append(
                TrackEditState(
                    id=track.id,
                    slot=track.slot,
                    display_name=track.display_name,
                    layers=layers,
                    keyframes=keyframes,
                )
            )

        return EditStateResponse(
            project=ProjectResponse.model_validate(project),
            tracks=track_states,
        )

