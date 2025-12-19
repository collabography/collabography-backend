from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import NotFoundError
from app.models import Track, SkeletonSource, SkeletonLayer, AssetStatus
from app.schemas.layer import LayerCreate, LayerUpdate, LayerResponse
from app.integrations.minio_client import get_presigned_put_url
from app.integrations.celery_client import enqueue_extract_skeleton
from datetime import timedelta


class LayersService:
    @staticmethod
    async def get_upload_url(
        track_id: int,
        filename: str,
        content_type: str = "video/mp4",
    ) -> tuple[str, str]:
        """레이어 업로드 presigned URL 발급"""
        # object_key 생성: videos/{track_id}/{filename}
        object_key = f"videos/{track_id}/{filename}"

        url = get_presigned_put_url(
            object_key=object_key,
            expires=timedelta(hours=1),
            content_type=content_type,
        )

        return url, object_key

    @staticmethod
    async def create_layer(db: AsyncSession, track_id: int, data: LayerCreate) -> LayerResponse:
        """레이어 생성 (VIDEO 또는 JSON 기반)"""
        # 트랙 확인
        track_result = await db.execute(select(Track).where(Track.id == track_id))
        track = track_result.scalar_one_or_none()

        if not track:
            raise NotFoundError("Track", track_id)

        # VIDEO 기반인지 JSON 기반인지 확인
        if data.video_object_key:
            # VIDEO 기반: SkeletonSource를 PROCESSING으로 생성하고 Celery 작업 enqueue
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
                start_sec=data.start_sec,
                end_sec=data.end_sec,
                priority=data.priority,
                label=data.label,
                created_at=datetime.utcnow(),
            )
            db.add(layer)
            await db.flush()

            # Celery 작업 enqueue
            enqueue_extract_skeleton(
                source_id=source.id,
                video_object_key=data.video_object_key,
                project_id=track.project_id,
                track_slot=track.slot,
            )

            await db.commit()
            await db.refresh(layer)
            await db.refresh(source)

        elif data.skeleton_object_key:
            # JSON 기반: SkeletonSource를 READY로 생성
            source = SkeletonSource(
                track_id=track_id,
                object_key=data.skeleton_object_key,
                fps=data.skeleton_fps,
                num_frames=data.skeleton_num_frames,
                num_joints=data.skeleton_num_joints,
                status=AssetStatus.READY,
                created_at=datetime.utcnow(),
            )
            db.add(source)
            await db.flush()

            # 레이어 생성
            layer = SkeletonLayer(
                track_id=track_id,
                skeleton_source_id=source.id,
                start_sec=data.start_sec,
                end_sec=data.end_sec,
                priority=data.priority,
                label=data.label,
                created_at=datetime.utcnow(),
            )
            db.add(layer)
            await db.commit()
            await db.refresh(layer)
            await db.refresh(source)

        else:
            raise ValueError("Either video_object_key or skeleton_object_key must be provided")

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

