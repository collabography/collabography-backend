from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AssetStatus


class SkeletonSource(Base):
    __tablename__ = "skeleton_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False)
    object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)  # MinIO key (READY일 때 유효)
    fps: Mapped[float | None] = mapped_column(nullable=True)
    num_frames: Mapped[int | None] = mapped_column(Integer, nullable=True)
    num_joints: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pose_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[AssetStatus] = mapped_column(default=AssetStatus.PROCESSING)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    track: Mapped["Track"] = relationship("Track", back_populates="sources")
    layers: Mapped[list["SkeletonLayer"]] = relationship("SkeletonLayer", back_populates="source")

