from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.asset import AssetType


class AssetCreate(BaseModel):
    job_id: uuid.UUID
    user_id: uuid.UUID
    asset_type: AssetType
    file_path: str
    file_url: str | None = None
    file_size: int | None = None
    duration: float | None = None
    metadata_: dict | None = Field(default=None, alias="metadata")
    tags: list[str] | None = None


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    job_id: uuid.UUID
    user_id: uuid.UUID
    asset_type: AssetType
    file_path: str
    file_url: str | None = None
    file_size: int | None = None
    duration: float | None = None
    metadata_: dict | None = Field(default=None, alias="metadata")
    tags: list | None = None
    created_at: datetime


class AssetList(BaseModel):
    items: list[AssetResponse]
    total: int
    page: int
    per_page: int
    pages: int
