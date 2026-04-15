from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalysisCreate(BaseModel):
    job_id: uuid.UUID
    asset_id: uuid.UUID | None = None
    hook_score: float = Field(ge=0, le=100)
    cta_score: float = Field(ge=0, le=100)
    pacing_score: float = Field(ge=0, le=100)
    platform_fit_score: float = Field(ge=0, le=100)
    engagement_score: float = Field(ge=0, le=100)
    explanation: str | None = None
    clip_selection_reason: str | None = None
    platform_recommendations: dict | None = None


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    asset_id: uuid.UUID | None = None
    hook_score: float
    cta_score: float
    pacing_score: float
    platform_fit_score: float
    engagement_score: float
    explanation: str | None = None
    clip_selection_reason: str | None = None
    platform_recommendations: dict | None = None
    created_at: datetime
