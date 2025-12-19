from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    slot: Mapped[int] = mapped_column(Integer, nullable=False)  # 1~3
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="tracks")
    layers: Mapped[list["SkeletonLayer"]] = relationship("SkeletonLayer", back_populates="track", cascade="all, delete-orphan")
    sources: Mapped[list["SkeletonSource"]] = relationship("SkeletonSource", back_populates="track", cascade="all, delete-orphan")
    keyframes: Mapped[list["TrackPositionKeyframe"]] = relationship("TrackPositionKeyframe", back_populates="track", cascade="all, delete-orphan")
    videos: Mapped[list["Video"]] = relationship("Video", back_populates="track", cascade="all, delete-orphan")

