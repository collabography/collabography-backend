from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SkeletonLayer(Base):
    __tablename__ = "skeleton_layers"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False)
    skeleton_source_id: Mapped[int] = mapped_column(ForeignKey("skeleton_sources.id", ondelete="RESTRICT"), nullable=False)
    start_sec: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    end_sec: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    track: Mapped["Track"] = relationship("Track", back_populates="layers")
    source: Mapped["SkeletonSource"] = relationship("SkeletonSource", back_populates="layers")

    # Indexes
    __table_args__ = (
        Index("idx_skeleton_layers_track_start", "track_id", "start_sec"),
        Index("idx_skeleton_layers_track_priority", "track_id", "priority"),
    )

