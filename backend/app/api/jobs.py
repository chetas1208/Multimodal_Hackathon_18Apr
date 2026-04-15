from __future__ import annotations

import math
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.bot_session import WorkflowType
from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate, JobList, JobResponse, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobList)
async def list_jobs(
    status: JobStatus | None = None,
    workflow_type: WorkflowType | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Job)
    count_query = select(func.count(Job.id))

    if status:
        query = query.where(Job.status == status)
        count_query = count_query.where(Job.status == status)
    if workflow_type:
        query = query.where(Job.workflow_type == workflow_type)
        count_query = count_query.where(Job.workflow_type == workflow_type)

    total = (await db.execute(count_query)).scalar() or 0
    pages = max(1, math.ceil(total / per_page))

    query = query.order_by(Job.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    items = list(result.scalars().all())

    return JobList(
        items=[JobResponse.model_validate(j) for j in items],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(payload: JobCreate, db: AsyncSession = Depends(get_db)):
    job = Job(
        user_id=payload.user_id,
        workflow_type=payload.workflow_type,
        status=JobStatus.queued,
        input_data=payload.input_data,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return JobResponse.model_validate(job)


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: uuid.UUID,
    payload: JobUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    if payload.status == JobStatus.processing and not job.started_at:
        job.started_at = datetime.now(timezone.utc)
    if payload.status in (JobStatus.completed, JobStatus.failed):
        job.completed_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(job)
    return JobResponse.model_validate(job)


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.delete(job)


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in (JobStatus.failed, JobStatus.completed):
        raise HTTPException(status_code=400, detail="Only failed or completed jobs can be retried")

    job.status = JobStatus.queued
    job.error_message = None
    job.started_at = None
    job.completed_at = None
    job.output_data = None

    await db.flush()
    await db.refresh(job)
    return JobResponse.model_validate(job)
