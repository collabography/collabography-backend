"""
스켈레톤 추출 Celery Task

이 파일은 나중에 실제 워커 구현으로 채워질 예정입니다.
현재는 단순히 성공 응답만 반환합니다.
"""
import logging

from worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="extract_skeleton", bind=True, max_retries=3)
def extract_skeleton_task(
    self,
    source_id: int,
    video_object_key: str,
    project_id: int,
    track_slot: int,
) -> dict:
    """
    스켈레톤 추출 작업 (Celery task)
    
    Args:
        source_id: SkeletonSource ID
        video_object_key: MinIO에 저장된 비디오 object key
        project_id: 프로젝트 ID
        track_slot: 트랙 슬롯 (1-3)
    
    Returns:
        작업 결과 딕셔너리
        
    TODO:
        - 실제 비디오에서 스켈레톤 추출 로직 구현
        - MinIO에서 비디오 다운로드
        - 스켈레톤 JSON 생성
        - MinIO에 JSON 업로드
        - DB에 SkeletonSource 상태 업데이트 (READY 또는 FAILED)
    """
    logger.info(
        f"Extract skeleton task started: source_id={source_id}, "
        f"video_object_key={video_object_key}, project_id={project_id}, track_slot={track_slot}"
    )

    # TODO: 실제 워커 구현이 여기에 들어갑니다
    # 현재는 단순히 성공 응답만 반환합니다
    
    # 예시: 실제 구현 시 이 부분을 채워넣으세요
    # try:
    #     # 1. MinIO에서 비디오 다운로드
    #     # 2. 스켈레톤 추출 (MediaPipe 등 사용)
    #     # 3. JSON 생성
    #     # 4. MinIO에 업로드
    #     # 5. DB 업데이트
    #     pass
    # except Exception as e:
    #     logger.error(f"Failed to extract skeleton: {e}")
    #     # DB 상태를 FAILED로 업데이트
    #     raise self.retry(exc=e, countdown=60)

    # 임시 응답 (나중에 실제 결과로 대체)
    result = {
        "status": "ok",
        "message": "Skeleton extraction task queued successfully",
        "source_id": source_id,
        "video_object_key": video_object_key,
        "project_id": project_id,
        "track_slot": track_slot,
    }

    logger.info(f"Extract skeleton task completed: source_id={source_id}")
    return result
