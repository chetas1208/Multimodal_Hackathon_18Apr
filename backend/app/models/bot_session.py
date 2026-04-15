from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class WorkflowType(str, enum.Enum):
    generate_video = "generate_video"
    clip_shorts = "clip_shorts"


class BotSession(TimestampMixin, Base):
    __tablename__ = "bot_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    workflow_type: Mapped[WorkflowType] = mapped_column(
        Enum(WorkflowType, name="workflow_type_enum"),
        nullable=False,
    )
    state: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    current_step: Mapped[str | None] = mapped_column(String(100), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="sessions")
