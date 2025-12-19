"""스켈레톤 추출 Celery Task."""

from __future__ import annotations

import asyncio
import logging
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any

from minio.error import S3Error
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.db.engine import get_engine
from app.models import AssetStatus, SkeletonSource
from app.storage.minio_client import get_minio_client
from worker.celery_app import celery_app
from worker.pipelines.pose_extractor import dump_json_to_bytes, extract_pose_to_json

logger = logging.getLogger(__name__)


def _ensure_bucket(bucket: str) -> None:
    client = get_minio_client()
    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket)


async def _update_source_success(
    sessionmaker: async_sessionmaker,
    source_id: int,
    object_key: str,
    meta: dict[str, Any],
) -> None:
    async with sessionmaker() as session:
        source = await session.get(SkeletonSource, source_id)
        if not source:
            raise RuntimeError(f"SkeletonSource not found: {source_id}")

        source.object_key = object_key
        source.fps = meta.get("fps")
        source.num_frames = meta.get("num_frames")
        source.num_joints = meta.get("num_joints")
        source.pose_model = meta.get("pose_model")
        source.status = AssetStatus.READY
        source.error_message = None

        await session.commit()


async def _update_source_failed(sessionmaker: async_sessionmaker, source_id: int, message: str) -> None:
    async with sessionmaker() as session:
        source = await session.get(SkeletonSource, source_id)
        if not source:
            return
        source.status = AssetStatus.FAILED
        source.error_message = message[:500]
        await session.commit()


def _build_object_key(project_id: int, track_slot: int, source_id: int) -> str:
    return f"skeleton/{project_id}/track_{track_slot}/{source_id}.json"


def _download_video_to_temp(video_object_key: str) -> Path:
    settings = get_settings()
    bucket = settings.minio_bucket
    if not bucket:
        raise RuntimeError("MinIO bucket not configured")

    client = get_minio_client()
    response = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(video_object_key).suffix) as tmp:
        try:
            response = client.get_object(bucket, video_object_key)
            tmp.write(response.read())
            tmp.flush()
        except S3Error as e:
            raise RuntimeError(f"Failed to download video from MinIO: {e}") from e
        finally:
            try:
                if response:
                    response.close()
            except Exception:
                pass
            try:
                if response:
                    response.release_conn()
            except Exception:
                pass
    return Path(tmp.name)


def _upload_json(object_key: str, payload: bytes) -> None:
    settings = get_settings()
    bucket = settings.minio_bucket
    if not bucket:
        raise RuntimeError("MinIO bucket not configured")

    client = get_minio_client()
    _ensure_bucket(bucket)
    client.put_object(
        bucket_name=bucket,
        object_name=object_key,
        data=BytesIO(payload),
        length=len(payload),
        content_type="application/json",
    )


def _get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


def _run_async(coro):
    """Celery 워커에서 async 함수를 안전하게 실행하는 헬퍼
    
    각 작업마다 독립적인 이벤트 루프를 생성하고,
    nest_asyncio를 조건부로 적용하여 중첩된 이벤트 루프를 허용합니다.
    """
    # 완전히 새로운 이벤트 루프 생성 (각 작업마다 독립적)
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    
    # nest_asyncio 적용 (uvloop가 아닌 경우에만, 한 번만)
    try:
        import nest_asyncio
        loop_type = type(new_loop).__name__
        if 'uvloop' not in loop_type.lower():
            # 표준 asyncio 루프인 경우에만 패치
            # 전역적으로 한 번만 적용 (이미 적용되었는지 확인)
            if not getattr(_run_async, '_nest_asyncio_applied', False):
                nest_asyncio.apply()
                _run_async._nest_asyncio_applied = True
    except (ValueError, AttributeError, ImportError, Exception):
        # 패치 실패해도 계속 진행 (단순 루프로 동작)
        pass
    
    try:
        return new_loop.run_until_complete(coro)
    finally:
        # 루프 정리
        try:
            # 모든 pending task 취소
            pending = asyncio.all_tasks(new_loop)
            if pending:
                for task in pending:
                    task.cancel()
                # 취소된 task들 완료 대기
                new_loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
        except Exception:
            pass
        finally:
            new_loop.close()
            asyncio.set_event_loop(None)


@celery_app.task(name="extract_skeleton", bind=True, max_retries=3)
def extract_skeleton_task(
    self,
    source_id: int,
    video_object_key: str,
    project_id: int,
    track_slot: int,
) -> dict:
    """스켈레톤 추출 작업."""
    logger.info(
        "Extract skeleton task started source_id=%s video=%s project_id=%s track_slot=%s",
        source_id,
        video_object_key,
        project_id,
        track_slot,
    )

    sessionmaker = _get_sessionmaker()

    try:
        # 1) Download video from MinIO
        video_path = _download_video_to_temp(video_object_key)

        # 2) Run pose extraction (MediaPipe)
        data = extract_pose_to_json(video_path=str(video_path))
        payload = dump_json_to_bytes(data)

        # 3) Upload skeleton JSON back to MinIO
        object_key = _build_object_key(project_id, track_slot, source_id)
        _upload_json(object_key, payload)

        # 4) Update DB -> READY
        meta = data.get("meta", {})
        _run_async(
            _update_source_success(
                sessionmaker,
                source_id,
                object_key,
                {
                    "fps": meta.get("fps"),
                    "num_frames": meta.get("num_frames"),
                    "num_joints": meta.get("num_joints"),
                    "pose_model": meta.get("pose_model"),
                },
            )
        )

        logger.info("Extract skeleton task completed source_id=%s object_key=%s", source_id, object_key)
        return {
            "status": "READY",
            "source_id": source_id,
            "object_key": object_key,
            "num_frames": meta.get("num_frames"),
            "fps": meta.get("fps"),
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("Extract skeleton failed source_id=%s: %s", source_id, exc)
        try:
            _run_async(_update_source_failed(sessionmaker, source_id, str(exc)))
        except Exception:
            logger.exception("Failed to mark source as FAILED for %s", source_id)
        raise self.retry(exc=exc, countdown=60)
    finally:
        try:
            if "video_path" in locals():
                Path(video_path).unlink(missing_ok=True)
        except Exception:
            logger.warning("Failed to clean temp video for source_id=%s", source_id)
