from datetime import datetime
from decimal import Decimal
from io import BytesIO

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import NotFoundError
from app.models import Track, SkeletonSource, SkeletonLayer, AssetStatus
from app.schemas.layer import LayerUpdate, LayerResponse
from app.integrations.minio_client import get_minio_client
from app.integrations.kafka_client import enqueue_skeleton_extraction
from app.core.config import get_settings


class LayersService:
    @staticmethod
    async def upload_layer(
        db: AsyncSession,
        track_id: int,
        file: UploadFile,
        start_sec: Decimal,
        end_sec: Decimal,
        priority: int = 0,
        label: str | None = None,
    ) -> LayerResponse:
        """레이어 파일 업로드, 프로젝트 연결, Kafka enqueue"""
        # 트랙 확인
        track_result = await db.execute(select(Track).where(Track.id == track_id))
        track = track_result.scalar_one_or_none()

        if not track:
            raise NotFoundError("Track", track_id)

        # object_key 생성: videos/{track_id}/{filename}
        object_key = f"videos/{track_id}/{file.filename}"

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
            content_type=file.content_type or "video/mp4",
        )

        # SkeletonSource를 PROCESSING으로 생성
        source = SkeletonSource(
            track_id=track_id,
            status=AssetStatus.PROCESSING,
            created_at=datetime.utcnow(),
        )
        db.add(source)
        await db.flush()

        # 레이어 생성
        layer = SkeletonLayer(
            track_id=track_id,
            skeleton_source_id=source.id,
            start_sec=start_sec,
            end_sec=end_sec,
            priority=priority,
            label=label,
            created_at=datetime.utcnow(),
        )
        db.add(layer)
        await db.flush()

        # Kafka에 스켈레톤 추출 작업 enqueue
        enqueue_skeleton_extraction(
            source_id=source.id,
            video_object_key=object_key,
            project_id=track.project_id,
            track_slot=track.slot,
        )

        await db.commit()
        await db.refresh(layer)
        await db.refresh(source)

        return LayersService._layer_to_response(layer, source)

    @staticmethod
    async def get_layer(db: AsyncSession, layer_id: int) -> LayerResponse:
        """레이어 조회 (상태 포함)"""
        result = await db.execute(
            select(SkeletonLayer)
            .where(SkeletonLayer.id == layer_id)
            .options(selectinload(SkeletonLayer.source))
        )
        layer = result.scalar_one_or_none()

        if not layer:
            raise NotFoundError("Layer", layer_id)

        return LayersService._layer_to_response(layer, layer.source)

    @staticmethod
    async def update_layer(db: AsyncSession, layer_id: int, data: LayerUpdate) -> LayerResponse:
        """레이어 업데이트"""
        result = await db.execute(
            select(SkeletonLayer)
            .where(SkeletonLayer.id == layer_id)
            .options(selectinload(SkeletonLayer.source))
        )
        layer = result.scalar_one_or_none()

        if not layer:
            raise NotFoundError("Layer", layer_id)

        if data.start_sec is not None:
            layer.start_sec = data.start_sec
        if data.end_sec is not None:
            layer.end_sec = data.end_sec
        if data.priority is not None:
            layer.priority = data.priority
        if data.label is not None:
            layer.label = data.label

        await db.commit()
        await db.refresh(layer)

        return LayersService._layer_to_response(layer, layer.source)

    @staticmethod
    async def delete_layer(db: AsyncSession, layer_id: int) -> None:
        """레이어 삭제"""
        result = await db.execute(select(SkeletonLayer).where(SkeletonLayer.id == layer_id))
        layer = result.scalar_one_or_none()

        if not layer:
            raise NotFoundError("Layer", layer_id)

        await db.delete(layer)
        await db.commit()

    @staticmethod
    def _layer_to_response(layer: SkeletonLayer, source: SkeletonSource) -> LayerResponse:
        """레이어와 소스를 응답 형식으로 변환"""
        return LayerResponse(
            id=layer.id,
            track_id=layer.track_id,
            skeleton_source_id=layer.skeleton_source_id,
            start_sec=layer.start_sec,
            end_sec=layer.end_sec,
            priority=layer.priority,
            label=layer.label,
            created_at=layer.created_at.isoformat(),
            source_status=source.status.value,
            source_object_key=source.object_key,
            source_fps=source.fps,
            source_num_frames=source.num_frames,
            source_num_joints=source.num_joints,
            source_error_message=source.error_message,
        )
