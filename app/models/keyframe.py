from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import InterpType


class TrackPositionKeyframe(Base):
    __tablename__ = "track_position_keyframes"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False)
    time_sec: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    x: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    y: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    interp: Mapped[InterpType] = mapped_column(default=InterpType.LINEAR)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    track: Mapped["Track"] = relationship("Track", back_populates="keyframes")

    # Constraints
    __table_args__ = (
        UniqueConstraint("track_id", "time_sec", name="uq_track_position_keyframes_track_time"),
        Index("idx_keyframes_track_time", "track_id", "time_sec"),
    )

