from celery import Celery

from app.core.config import get_settings

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
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Task 모듈 자동 발견
celery_app.autodiscover_tasks(["worker.tasks"])
