import json
import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import get_settings
from app.models import SkeletonSource, AssetStatus
from app.integrations.minio_client import get_minio_client
from worker.celery_app import celery_app
from worker.pipelines.skeleton_writer import create_dummy_skeleton_json

logger = logging.getLogger(__name__)


@celery_app.task(name="extract_skeleton", bind=True, max_retries=3)
def extract_skeleton_task(
    self,
    source_id: int,
    video_object_key: str,
    project_id: int,
    track_slot: int,
) -> dict:
    """스켈레톤 추출 작업 (Celery task)"""
    settings = get_settings()
    engine = create_async_engine(settings.sqlalchemy_database_url(), pool_pre_ping=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    import asyncio

    try:
        # 동기 함수에서 비동기 세션 사용을 위해 run_async 사용
        result = asyncio.run(_extract_skeleton_async(
            async_session=async_session,
            source_id=source_id,
            video_object_key=video_object_key,
            project_id=project_id,
            track_slot=track_slot,
        ))

        return result
    except Exception as exc:
        logger.error(f"Failed to extract skeleton for source_id={source_id}: {exc}", exc_info=True)
        # 실패 시 DB 상태 업데이트
        try:
            asyncio.run(_mark_source_failed(async_session, source_id, str(exc)))
        except Exception as e:
            logger.error(f"Failed to mark source as failed: {e}")
        raise self.retry(exc=exc, countdown=60)  # 1분 후 재시도
    finally:
        asyncio.run(engine.dispose())


async def _extract_skeleton_async(
    async_session: async_sessionmaker[AsyncSession],
    source_id: int,
    video_object_key: str,
    project_id: int,
    track_slot: int,
) -> dict:
    """비동기 스켈레톤 추출 로직"""
    async with async_session() as session:
        # Source 조회
        result = await session.execute(select(SkeletonSource).where(SkeletonSource.id == source_id))
        source = result.scalar_one_or_none()

        if not source:
            raise ValueError(f"SkeletonSource {source_id} not found")

        if source.status != AssetStatus.PROCESSING:
            logger.warning(f"Source {source_id} is not in PROCESSING status: {source.status}")
            return {"status": "skipped", "reason": "not_processing"}

        try:
            # MinIO에서 영상 다운로드 (실제로는 스트리밍 또는 임시 파일 사용)
            # MVP에서는 더미 데이터 생성
            logger.info(f"Extracting skeleton from video: {video_object_key}")

            # 더미 스켈레톤 JSON 생성 (실제로는 pose_extractor 사용)
            skeleton_data = create_dummy_skeleton_json(
                fps=30.0,
                num_frames=100,
                num_joints=33,
            )

            # MinIO에 JSON 업로드
            object_key = f"skeleton/{project_id}/track_{track_slot}/{source_id}.json"
            minio_client = get_minio_client()
            settings = get_settings()
            bucket = settings.minio_bucket

            if not bucket:
                raise ValueError("MinIO bucket not configured")

            # JSON을 bytes로 변환
            json_bytes = json.dumps(skeleton_data).encode("utf-8")
            from io import BytesIO

            minio_client.put_object(
                bucket_name=bucket,
                object_name=object_key,
                data=BytesIO(json_bytes),
                length=len(json_bytes),
                content_type="application/json",
            )

            # DB 업데이트
            source.object_key = object_key
            source.fps = skeleton_data["meta"]["fps"]
            source.num_frames = skeleton_data["meta"]["num_frames"]
            source.num_joints = skeleton_data["meta"]["num_joints"]
            source.pose_model = skeleton_data["meta"].get("pose_model", "dummy")
            source.status = AssetStatus.READY
            source.error_message = None

            await session.commit()
            await session.refresh(source)

            logger.info(f"Successfully extracted skeleton for source_id={source_id}, object_key={object_key}")

            return {
                "status": "success",
                "source_id": source_id,
                "object_key": object_key,
            }

        except Exception as e:
            # 실패 처리
            source.status = AssetStatus.FAILED
            source.error_message = str(e)
            await session.commit()
            raise


async def _mark_source_failed(
    async_session: async_sessionmaker[AsyncSession],
    source_id: int,
    error_message: str,
) -> None:
    """소스 실패 상태로 마킹"""
    async with async_session() as session:
        result = await session.execute(select(SkeletonSource).where(SkeletonSource.id == source_id))
        source = result.scalar_one_or_none()

        if source:
            source.status = AssetStatus.FAILED
            source.error_message = error_message
            await session.commit()

