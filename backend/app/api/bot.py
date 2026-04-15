from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.activity_log import ActivityLog, LogLevel
from app.models.bot_session import BotSession, WorkflowType
from app.models.job import Job, JobStatus
from app.models.user import User
from app.models.workflow_request import SourceType, WorkflowRequest
from app.schemas.bot import TelegramWebhookPayload, WorkflowStartRequest
from app.schemas.job import JobResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bot", tags=["bot"])


async def _get_or_create_user(db: AsyncSession, telegram_id: int, username: str | None = None, first_name: str | None = None) -> User:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(telegram_id=telegram_id, username=username, first_name=first_name)
        db.add(user)
        await db.flush()
        await db.refresh(user)
    return user


@router.post("/webhook/telegram")
async def telegram_webhook(payload: TelegramWebhookPayload, db: AsyncSession = Depends(get_db)):
    if not payload.message or not payload.message.text:
        return {"ok": True, "action": "ignored"}

    msg = payload.message
    from_user = msg.from_
    tg_id = from_user.id if from_user else msg.chat.id
    username = from_user.username if from_user else None
    first_name = from_user.first_name if from_user else None

    user = await _get_or_create_user(db, tg_id, username, first_name)

    text = msg.text.strip().lower()
    if text in ("/start", "hi", "hello"):
        return {
            "ok": True,
            "reply": (
                "Welcome to Marketing Studio Bot!\n\n"
                "Commands:\n"
                "/generate - Create a promo video\n"
                "/clip - Extract clips from a YouTube video\n"
                "/status - Check your latest job"
            ),
        }

    if text.startswith("/generate"):
        session = BotSession(
            user_id=user.id,
            workflow_type=WorkflowType.generate_video,
            state={"step": "awaiting_product_info"},
            current_step="awaiting_product_info",
        )
        db.add(session)
        return {"ok": True, "reply": "Let's create a promo video! Send me a product URL or describe your product."}

    if text.startswith("/clip"):
        session = BotSession(
            user_id=user.id,
            workflow_type=WorkflowType.clip_shorts,
            state={"step": "awaiting_youtube_url"},
            current_step="awaiting_youtube_url",
        )
        db.add(session)
        return {"ok": True, "reply": "Send me a YouTube URL and I'll extract the best clips for shorts."}

    if text.startswith("/status"):
        result = await db.execute(
            select(Job).where(Job.user_id == user.id).order_by(Job.created_at.desc()).limit(1)
        )
        job = result.scalar_one_or_none()
        if job:
            return {"ok": True, "reply": f"Latest job: {job.workflow_type.value} — Status: {job.status.value}"}
        return {"ok": True, "reply": "No jobs found. Use /generate or /clip to get started."}

    return {"ok": True, "reply": "I didn't understand that. Try /generate, /clip, or /status."}


@router.post("/webhook/photon")
async def photon_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    logger.info("Photon webhook received: %s", body)
    return {"ok": True, "message": "Photon webhook acknowledged"}


@router.post("/start-workflow", response_model=JobResponse)
async def start_workflow(payload: WorkflowStartRequest, db: AsyncSession = Depends(get_db)):
    user = await _get_or_create_user(db, payload.telegram_id)

    source_type = SourceType.text
    if payload.product_url or payload.youtube_url:
        source_type = SourceType.url

    job = Job(
        user_id=user.id,
        workflow_type=payload.workflow_type,
        status=JobStatus.queued,
        input_data={
            "product_url": payload.product_url,
            "product_text": payload.product_text,
            "youtube_url": payload.youtube_url,
        },
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)

    wf_req = WorkflowRequest(
        job_id=job.id,
        user_id=user.id,
        workflow_type=payload.workflow_type,
        product_url=payload.product_url,
        product_text=payload.product_text,
        youtube_url=payload.youtube_url,
        source_type=source_type,
        raw_input=payload.model_dump(),
    )
    db.add(wf_req)

    activity = ActivityLog(
        user_id=user.id,
        job_id=job.id,
        event_type="workflow_started",
        message=f"Started {payload.workflow_type.value} workflow",
        level=LogLevel.info,
    )
    db.add(activity)

    return JobResponse.model_validate(job)
