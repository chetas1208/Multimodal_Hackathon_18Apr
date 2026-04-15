from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.bot_session import WorkflowType
from app.models.job import JobStatus


class JobCreate(BaseModel):
    user_id: uuid.UUID
    workflow_type: WorkflowType
    input_data: dict = Field(default_factory=dict)


class JobUpdate(BaseModel):
    status: JobStatus | None = None
    output_data: dict | None = None
    error_message: str | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    workflow_type: WorkflowType
    status: JobStatus
    input_data: dict
    output_data: dict | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class JobList(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    per_page: int
    pages: int
