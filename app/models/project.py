from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    music_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    music_duration_sec: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    music_bpm: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tracks: Mapped[list["Track"]] = relationship("Track", back_populates="project", cascade="all, delete-orphan")

