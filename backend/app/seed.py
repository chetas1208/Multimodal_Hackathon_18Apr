from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog, LogLevel
from app.models.analysis import Analysis
from app.models.asset import Asset, AssetType
from app.models.bot_session import WorkflowType
from app.models.job import Job, JobStatus


async def seed_demo_data(db: AsyncSession) -> dict:
    """Populate the database with realistic demo data. Returns summary counts."""
    from app.models.user import User

    now = datetime.now(timezone.utc)

    # --- Users ---
    user1 = User(telegram_id=100001, username="demo_alice", first_name="Alice")
    user2 = User(telegram_id=100002, username="demo_bob", first_name="Bob")
    db.add_all([user1, user2])
    await db.flush()

    # --- Jobs ---
    jobs_data = [
        {"user": user1, "wf": WorkflowType.generate_video, "status": JobStatus.completed, "ago_h": 24},
        {"user": user1, "wf": WorkflowType.clip_shorts, "status": JobStatus.completed, "ago_h": 18},
        {"user": user2, "wf": WorkflowType.generate_video, "status": JobStatus.processing, "ago_h": 2},
        {"user": user2, "wf": WorkflowType.clip_shorts, "status": JobStatus.queued, "ago_h": 1},
        {"user": user1, "wf": WorkflowType.generate_video, "status": JobStatus.failed, "ago_h": 48},
    ]

    jobs: list[Job] = []
    for jd in jobs_data:
        created = now - timedelta(hours=jd["ago_h"])
        job = Job(
            user_id=jd["user"].id,
            workflow_type=jd["wf"],
            status=jd["status"],
            input_data={
                "product_url": "https://example.com/product" if jd["wf"] == WorkflowType.generate_video else "",
                "youtube_url": "https://youtube.com/watch?v=dQw4w9WgXcQ" if jd["wf"] == WorkflowType.clip_shorts else "",
                "product_text": "Amazing Skincare Serum — 30% off today!",
            },
            started_at=created + timedelta(seconds=5) if jd["status"] != JobStatus.queued else None,
            completed_at=created + timedelta(minutes=3) if jd["status"] in (JobStatus.completed, JobStatus.failed) else None,
            error_message="ffmpeg timeout on large file" if jd["status"] == JobStatus.failed else None,
        )
        db.add(job)
        jobs.append(job)
    await db.flush()

    # --- Assets ---
    asset_specs = [
        {"job": jobs[0], "user": user1, "type": AssetType.video, "dur": 12.5, "tags": ["promo", "generated"]},
        {"job": jobs[0], "user": user1, "type": AssetType.thumbnail, "dur": None, "tags": ["thumbnail"]},
        {"job": jobs[1], "user": user1, "type": AssetType.video, "dur": 28.0, "tags": ["clip", "shorts", "clip_1"]},
        {"job": jobs[1], "user": user1, "type": AssetType.video, "dur": 32.5, "tags": ["clip", "shorts", "clip_2"]},
        {"job": jobs[1], "user": user1, "type": AssetType.video, "dur": 25.0, "tags": ["clip", "shorts", "clip_3"]},
        {"job": jobs[1], "user": user1, "type": AssetType.subtitle, "dur": None, "tags": ["srt"]},
        {"job": jobs[2], "user": user2, "type": AssetType.video, "dur": 10.0, "tags": ["promo", "wip"]},
        {"job": jobs[2], "user": user2, "type": AssetType.image, "dur": None, "tags": ["product_image"]},
    ]

    assets: list[Asset] = []
    for i, spec in enumerate(asset_specs):
        asset = Asset(
            job_id=spec["job"].id,
            user_id=spec["user"].id,
            asset_type=spec["type"],
            file_path=f"./media/demo/asset_{i+1}.{'mp4' if spec['type'] == AssetType.video else 'png'}",
            file_url=f"/media/demo/asset_{i+1}.{'mp4' if spec['type'] == AssetType.video else 'png'}",
            file_size=(spec["dur"] or 1) * 50000,
            duration=spec["dur"],
            tags=spec["tags"],
        )
        db.add(asset)
        assets.append(asset)
    await db.flush()

    # --- Analyses ---
    analysis_specs = [
        {"job": jobs[0], "asset": assets[0], "hook": 82.5, "cta": 78.0, "pacing": 85.0, "platform": 92.0, "engage": 84.3},
        {"job": jobs[1], "asset": assets[2], "hook": 91.0, "cta": 65.0, "pacing": 88.5, "platform": 95.0, "engage": 85.1},
        {"job": jobs[1], "asset": assets[3], "hook": 74.5, "cta": 70.0, "pacing": 79.0, "platform": 90.0, "engage": 78.4},
        {"job": jobs[1], "asset": assets[4], "hook": 68.0, "cta": 55.0, "pacing": 82.0, "platform": 88.0, "engage": 73.2},
        {"job": jobs[4], "asset": None, "hook": 45.0, "cta": 30.0, "pacing": 60.0, "platform": 50.0, "engage": 46.2},
    ]

    for spec in analysis_specs:
        a = Analysis(
            job_id=spec["job"].id,
            asset_id=spec["asset"].id if spec["asset"] else None,
            hook_score=spec["hook"],
            cta_score=spec["cta"],
            pacing_score=spec["pacing"],
            platform_fit_score=spec["platform"],
            engagement_score=spec["engage"],
            explanation=(
                "Strong opening hook grabs attention. CTA present but could be more direct. "
                "Pacing is solid for short-form. Great platform fit for Reels and TikTok."
            ),
            clip_selection_reason="Selected for high hook strength in opening segment" if spec["asset"] else None,
            platform_recommendations={
                "tiktok": {"suitable": True, "notes": "Great hook and pacing for TikTok."},
                "instagram_reels": {"suitable": True, "notes": "Under 90s — ideal for Reels."},
                "youtube_shorts": {"suitable": True, "notes": "Vertical format ready."},
            },
        )
        db.add(a)

    # --- Activity Logs ---
    log_entries = [
        {"user": user1, "job": jobs[0], "event": "workflow_started", "msg": "Started generate_video workflow", "level": LogLevel.info, "ago_h": 24},
        {"user": user1, "job": jobs[0], "event": "job_processing", "msg": "Video generation in progress", "level": LogLevel.info, "ago_h": 24},
        {"user": user1, "job": jobs[0], "event": "job_completed", "msg": "Promo video generated successfully", "level": LogLevel.info, "ago_h": 23},
        {"user": user1, "job": jobs[1], "event": "workflow_started", "msg": "Started clip_shorts workflow", "level": LogLevel.info, "ago_h": 18},
        {"user": user1, "job": jobs[1], "event": "job_completed", "msg": "Extracted 3 clips from YouTube video", "level": LogLevel.info, "ago_h": 17},
        {"user": user2, "job": jobs[2], "event": "workflow_started", "msg": "Started generate_video workflow", "level": LogLevel.info, "ago_h": 2},
        {"user": user2, "job": jobs[2], "event": "job_processing", "msg": "Processing video generation", "level": LogLevel.info, "ago_h": 2},
        {"user": user2, "job": jobs[3], "event": "workflow_started", "msg": "Started clip_shorts workflow", "level": LogLevel.info, "ago_h": 1},
        {"user": user1, "job": jobs[4], "event": "job_failed", "msg": "Video generation failed: ffmpeg timeout", "level": LogLevel.error, "ago_h": 48},
        {"user": None, "job": None, "event": "system_startup", "msg": "Marketing Studio Bot backend started", "level": LogLevel.info, "ago_h": 72},
    ]

    for entry in log_entries:
        log = ActivityLog(
            user_id=entry["user"].id if entry["user"] else None,
            job_id=entry["job"].id if entry["job"] else None,
            event_type=entry["event"],
            message=entry["msg"],
            level=entry["level"],
        )
        db.add(log)

    await db.flush()

    return {
        "users": 2,
        "jobs": len(jobs),
        "assets": len(assets),
        "analyses": len(analysis_specs),
        "activity_logs": len(log_entries),
    }
