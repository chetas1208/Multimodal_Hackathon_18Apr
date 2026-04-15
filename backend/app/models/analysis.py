from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class Analysis(TimestampMixin, Base):
    __tablename__ = "analyses"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    asset_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    hook_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    cta_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    pacing_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    platform_fit_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    engagement_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    clip_selection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform_recommendations: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    job = relationship("Job", back_populates="analyses")
    asset = relationship("Asset", back_populates="analysis")
