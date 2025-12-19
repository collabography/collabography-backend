from celery import Celery
from celery.signals import worker_process_init

from app.core.config import get_settings

# 워커 프로세스 시작 시 nest_asyncio 적용 (한 번만)
@worker_process_init.connect
def init_worker(**kwargs):
    """워커 프로세스 초기화 시 nest_asyncio 적용"""
    try:
        import nest_asyncio
        import asyncio
        
        # 현재 이벤트 루프 확인
        try:
            loop = asyncio.get_event_loop()
            loop_type = type(loop).__name__
            # uvloop가 아닌 경우에만 적용
            if 'uvloop' not in loop_type.lower():
                nest_asyncio.apply()
        except RuntimeError:
            # 이벤트 루프가 없으면 나중에 적용
            nest_asyncio.apply()
    except (ImportError, ValueError, AttributeError):
        # nest_asyncio 적용 실패해도 계속 진행
        pass

settings = get_settings()

celery_app = Celery(
    "collabography_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["worker.tasks.extract_skeleton"],
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

