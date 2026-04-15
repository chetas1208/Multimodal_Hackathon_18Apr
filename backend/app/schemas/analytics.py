from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float
    label: str | None = None


class WorkflowBreakdown(BaseModel):
    workflow_type: str
    count: int
    percentage: float


class ActivityItem(BaseModel):
    event_type: str
    message: str
    level: str
    created_at: datetime
    user_id: str | None = None
    job_id: str | None = None


class DashboardStats(BaseModel):
    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    processing_jobs: int = 0
    total_assets: int = 0
    total_users: int = 0
    avg_hook_score: float = 0.0
    avg_engagement_score: float = 0.0
    workflow_breakdown: list[WorkflowBreakdown] = []


class ActivitySummary(BaseModel):
    recent_activity: list[ActivityItem] = []
    jobs_over_time: list[TimeSeriesPoint] = []
