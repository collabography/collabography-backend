from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AssetStatus


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    duration_sec: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    fps: Mapped[float | None] = mapped_column(nullable=True)
    status: Mapped[AssetStatus] = mapped_column(default=AssetStatus.UPLOADED)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    track: Mapped["Track"] = relationship("Track", back_populates="videos")

