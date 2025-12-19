from datetime import datetime
from decimal import Decimal
from io import BytesIO

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models import Project
from app.integrations.minio_client import get_minio_client
from app.core.config import get_settings


class MusicService:
    @staticmethod
    async def upload_music(
        db: AsyncSession,
        project_id: int,
        file: UploadFile,
        duration_sec: Decimal | None = None,
        bpm: Decimal | None = None,
    ) -> tuple[str, Decimal | None, Decimal | None]:
        """음악 파일 업로드 및 프로젝트에 연결"""
        # 프로젝트 확인
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise NotFoundError("Project", project_id)

        # object_key 생성: music/{project_id}/{filename}
        object_key = f"music/{project_id}/{file.filename}"

        # MinIO에 업로드
        settings = get_settings()
        minio_client = get_minio_client()
        bucket = settings.minio_bucket

        if not bucket:
            raise ValueError("MinIO bucket not configured")

        # 파일 읽기
        file_content = await file.read()

        # MinIO에 업로드
        minio_client.put_object(
            bucket_name=bucket,
            object_name=object_key,
            data=BytesIO(file_content),
            length=len(file_content),
            content_type=file.content_type or "audio/mpeg",
        )

        # 프로젝트에 연결
        project.music_object_key = object_key
        project.music_duration_sec = duration_sec
        project.music_bpm = bpm
        project.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(project)

        return object_key, duration_sec, bpm
