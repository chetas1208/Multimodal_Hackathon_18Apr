from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    sessions = relationship("BotSession", back_populates="user", lazy="selectin")
    jobs = relationship("Job", back_populates="user", lazy="selectin")
    assets = relationship("Asset", back_populates="user", lazy="selectin")
    workflow_requests = relationship("WorkflowRequest", back_populates="user", lazy="selectin")
    activity_logs = relationship("ActivityLog", back_populates="user", lazy="selectin")
