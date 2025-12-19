from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models import Track, TrackPositionKeyframe
from app.schemas.keyframe import KeyframeUpsert, KeyframeResponse


class KeyframesService:
    @staticmethod
    async def upsert_keyframes(db: AsyncSession, track_id: int, data: KeyframeUpsert) -> list[KeyframeResponse]:
        """키프레임 전체 교체 (upsert)"""
        # 트랙 확인
        track_result = await db.execute(select(Track).where(Track.id == track_id))
        track = track_result.scalar_one_or_none()

        if not track:
            raise NotFoundError("Track", track_id)

        # 기존 키프레임 삭제
        await db.execute(delete(TrackPositionKeyframe).where(TrackPositionKeyframe.track_id == track_id))

        # 새 키프레임 생성
        keyframes = []
        for item in data.keyframes:
            kf = TrackPositionKeyframe(
                track_id=track_id,
                time_sec=item.time_sec,
                x=item.x,
                y=item.y,
                interp=item.interp,
                created_at=datetime.utcnow(),
            )
            db.add(kf)
            keyframes.append(kf)

        await db.commit()

        # 새로 생성된 키프레임 조회
        for kf in keyframes:
            await db.refresh(kf)

        return [KeyframeResponse.model_validate(kf) for kf in keyframes]

    @staticmethod
    async def get_keyframes(db: AsyncSession, track_id: int) -> list[KeyframeResponse]:
        """키프레임 목록 조회"""
        result = await db.execute(
            select(TrackPositionKeyframe)
            .where(TrackPositionKeyframe.track_id == track_id)
            .order_by(TrackPositionKeyframe.time_sec)
        )
        keyframes = result.scalars().all()

        return [KeyframeResponse.model_validate(kf) for kf in keyframes]

