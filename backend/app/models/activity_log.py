from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class LogLevel(str, enum.Enum):
    info = "info"
    warning = "warning"
    error = "error"


class ActivityLog(TimestampMixin, Base):
    __tablename__ = "activity_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    level: Mapped[LogLevel] = mapped_column(
        Enum(LogLevel, name="log_level_enum"),
        default=LogLevel.info,
        nullable=False,
    )

    user = relationship("User", back_populates="activity_logs")
    job = relationship("Job", back_populates="activity_logs")
