from functools import lru_cache

from celery import Celery

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_celery_app() -> Celery:
    """Celery 앱 인스턴스 반환"""
    settings = get_settings()

    celery_app = Celery(
        "collabography_worker",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )

    return celery_app


def enqueue_extract_skeleton(
    source_id: int,
    video_object_key: str,
    project_id: int,
    track_slot: int,
) -> str:
    """스켈레톤 추출 작업을 큐에 추가"""
    celery_app = get_celery_app()

    # worker/tasks/extract_skeleton.py의 task를 import
    # 동적 import로 순환 참조 방지
    from worker.tasks.extract_skeleton import extract_skeleton_task

    task = extract_skeleton_task.delay(
        source_id=source_id,
        video_object_key=video_object_key,
        project_id=project_id,
        track_slot=track_slot,
    )

    return task.id

