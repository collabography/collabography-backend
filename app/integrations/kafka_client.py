import json
import logging
from functools import lru_cache

from kafka import KafkaProducer
from kafka.errors import KafkaError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_kafka_producer() -> KafkaProducer | None:
    """Kafka Producer 인스턴스 반환"""
    settings = get_settings()

    try:
        producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: str(k).encode("utf-8") if k else None,
        )
        return producer
    except Exception as e:
        logger.warning(f"Failed to create Kafka producer: {e}. Kafka features will be disabled.")
        return None


def enqueue_skeleton_extraction(
    source_id: int,
    video_object_key: str,
    project_id: int,
    track_slot: int,
) -> bool:
    """스켈레톤 추출 작업을 Kafka에 enqueue"""
    producer = get_kafka_producer()

    if not producer:
        logger.error("Kafka producer is not available")
        return False

    try:
        message = {
            "source_id": source_id,
            "video_object_key": video_object_key,
            "project_id": project_id,
            "track_slot": track_slot,
        }

        future = producer.send(
            get_settings().kafka_topic_skeleton_extraction,
            key=str(source_id),
            value=message,
        )

        # 비동기 전송이므로 즉시 반환 (필요시 future.get()으로 확인 가능)
        logger.info(f"Enqueued skeleton extraction task for source_id={source_id}")
        return True

    except KafkaError as e:
        logger.error(f"Failed to enqueue skeleton extraction task: {e}")
        return False


def close_producer() -> None:
    """Kafka Producer 종료"""
    producer = get_kafka_producer()
    if producer:
        producer.close()

