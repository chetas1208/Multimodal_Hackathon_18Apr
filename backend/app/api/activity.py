from __future__ import annotations

import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.activity_log import ActivityLog, LogLevel

router = APIRouter(prefix="/activity", tags=["activity"])


class ActivityLogResponse(ActivityLog.__class__):
    pass


from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ActivityLogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None = None
    job_id: uuid.UUID | None = None
    event_type: str
    message: str
    metadata_: dict | None = None
    level: LogLevel
    created_at: datetime


class ActivityLogList(BaseModel):
    items: list[ActivityLogItem]
    total: int
    page: int
    per_page: int


@router.get("", response_model=ActivityLogList)
async def list_activity(
    user_id: uuid.UUID | None = None,
    job_id: uuid.UUID | None = None,
    level: LogLevel | None = None,
    event_type: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(ActivityLog)
    count_query = select(func.count(ActivityLog.id))

    if user_id:
        query = query.where(ActivityLog.user_id == user_id)
        count_query = count_query.where(ActivityLog.user_id == user_id)
    if job_id:
        query = query.where(ActivityLog.job_id == job_id)
        count_query = count_query.where(ActivityLog.job_id == job_id)
    if level:
        query = query.where(ActivityLog.level == level)
        count_query = count_query.where(ActivityLog.level == level)
    if event_type:
        query = query.where(ActivityLog.event_type == event_type)
        count_query = count_query.where(ActivityLog.event_type == event_type)

    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(ActivityLog.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    items = list(result.scalars().all())

    return ActivityLogList(
        items=[ActivityLogItem.model_validate(a) for a in items],
        total=total,
        page=page,
        per_page=per_page,
    )
