from __future__ import annotations

import enum
import uuid

from sqlalchemy import BigInteger, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class AssetType(str, enum.Enum):
    video = "video"
    image = "image"
    subtitle = "subtitle"
    thumbnail = "thumbnail"


class Asset(TimestampMixin, Base):
    __tablename__ = "assets"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType, name="asset_type_enum"),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)

    job = relationship("Job", back_populates="assets")
    user = relationship("User", back_populates="assets")
    analysis = relationship("Analysis", back_populates="asset", uselist=False, lazy="selectin")
