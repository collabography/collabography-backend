from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models import Project
from app.schemas.music import MusicCommit
from app.integrations.minio_client import get_presigned_put_url
from datetime import timedelta


class MusicService:
    @staticmethod
    async def get_upload_url(
        project_id: int,
        filename: str,
        content_type: str = "audio/mpeg",
    ) -> tuple[str, str]:
        """음악 업로드 presigned URL 발급"""
        # object_key 생성: music/{project_id}/{filename}
        object_key = f"music/{project_id}/{filename}"

        url = get_presigned_put_url(
            object_key=object_key,
            expires=timedelta(hours=1),
            content_type=content_type,
        )

        return url, object_key

    @staticmethod
    async def commit_music(db: AsyncSession, project_id: int, data: MusicCommit) -> None:
        """음악 업로드 완료 후 프로젝트에 연결"""
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise NotFoundError("Project", project_id)

        project.music_object_key = data.object_key
        project.music_duration_sec = data.duration_sec
        project.music_bpm = data.bpm
        project.updated_at = datetime.utcnow()

        await db.commit()

