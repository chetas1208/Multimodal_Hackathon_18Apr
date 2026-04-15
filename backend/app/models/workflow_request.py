from __future__ import annotations

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.bot_session import WorkflowType


class SourceType(str, enum.Enum):
    url = "url"
    upload = "upload"
    text = "text"


class WorkflowRequest(TimestampMixin, Base):
    __tablename__ = "workflow_requests"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    workflow_type: Mapped[WorkflowType] = mapped_column(
        Enum(WorkflowType, name="workflow_type_enum", create_type=False),
        nullable=False,
    )
    product_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    youtube_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type_enum"),
        nullable=False,
    )
    raw_input: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    job = relationship("Job", back_populates="workflow_request")
    user = relationship("User", back_populates="workflow_requests")
