from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.activity_log import ActivityLog
from app.models.analysis import Analysis
from app.models.asset import Asset
from app.models.job import Job, JobStatus
from app.models.user import User
from app.schemas.analytics import (
    ActivityItem,
    ActivitySummary,
    DashboardStats,
    TimeSeriesPoint,
    WorkflowBreakdown,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    total_jobs = (await db.execute(select(func.count(Job.id)))).scalar() or 0
    completed = (
        await db.execute(select(func.count(Job.id)).where(Job.status == JobStatus.completed))
    ).scalar() or 0
    failed = (
        await db.execute(select(func.count(Job.id)).where(Job.status == JobStatus.failed))
    ).scalar() or 0
    processing = (
        await db.execute(select(func.count(Job.id)).where(Job.status == JobStatus.processing))
    ).scalar() or 0
    total_assets = (await db.execute(select(func.count(Asset.id)))).scalar() or 0
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0

    avg_hook = (await db.execute(select(func.avg(Analysis.hook_score)))).scalar() or 0.0
    avg_engagement = (
        await db.execute(select(func.avg(Analysis.engagement_score)))
    ).scalar() or 0.0

    wf_rows = (
        await db.execute(
            select(Job.workflow_type, func.count(Job.id)).group_by(Job.workflow_type)
        )
    ).all()

    breakdown = []
    for wf_type, count in wf_rows:
        pct = (count / total_jobs * 100) if total_jobs else 0.0
        breakdown.append(WorkflowBreakdown(workflow_type=wf_type.value, count=count, percentage=round(pct, 1)))

    return DashboardStats(
        total_jobs=total_jobs,
        completed_jobs=completed,
        failed_jobs=failed,
        processing_jobs=processing,
        total_assets=total_assets,
        total_users=total_users,
        avg_hook_score=round(float(avg_hook), 1),
        avg_engagement_score=round(float(avg_engagement), 1),
        workflow_breakdown=breakdown,
    )


@router.get("/activity", response_model=ActivitySummary)
async def activity_timeline(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(50)
    )
    logs = result.scalars().all()

    recent = [
        ActivityItem(
            event_type=log.event_type,
            message=log.message,
            level=log.level.value,
            created_at=log.created_at,
            user_id=str(log.user_id) if log.user_id else None,
            job_id=str(log.job_id) if log.job_id else None,
        )
        for log in logs
    ]

    time_result = await db.execute(
        select(
            func.date_trunc("hour", Job.created_at).label("bucket"),
            func.count(Job.id),
        )
        .group_by("bucket")
        .order_by("bucket")
        .limit(168)
    )
    time_series = [
        TimeSeriesPoint(timestamp=row[0], value=float(row[1]))
        for row in time_result.all()
    ]

    return ActivitySummary(recent_activity=recent, jobs_over_time=time_series)
