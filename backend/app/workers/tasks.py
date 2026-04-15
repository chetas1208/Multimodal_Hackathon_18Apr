from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models.activity_log import ActivityLog, LogLevel
from app.models.analysis import Analysis
from app.models.asset import Asset, AssetType
from app.models.job import Job, JobStatus
from app.services.analysis import AnalysisService
from app.services.clip_extractor import ClipExtractorService
from app.services.transcription import TranscriptionService
from app.services.url_scraper import scrape_product
from app.services.video_generator import VideoGeneratorService
from app.services.youtube import YouTubeService
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

sync_url = settings.DATABASE_URL
if sync_url.startswith("postgresql+asyncpg://"):
    sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://", 1)

sync_engine = create_engine(sync_url)
SyncSession = sessionmaker(bind=sync_engine)


def _log_activity(
    db: Session,
    *,
    user_id: uuid.UUID | None = None,
    job_id: uuid.UUID | None = None,
    event_type: str,
    message: str,
    level: LogLevel = LogLevel.info,
    metadata: dict | None = None,
) -> None:
    log = ActivityLog(
        user_id=user_id,
        job_id=job_id,
        event_type=event_type,
        message=message,
        level=level,
    )
    if metadata:
        log.metadata_ = metadata
    db.add(log)


@celery_app.task(name="app.workers.tasks.process_generate_video", bind=True, max_retries=2)
def process_generate_video(self, job_id: str) -> dict:
    job_uuid = uuid.UUID(job_id)

    with SyncSession() as db:
        job = db.execute(select(Job).where(Job.id == job_uuid)).scalar_one_or_none()
        if not job:
            logger.error("Job %s not found", job_id)
            return {"error": "Job not found"}

        job.status = JobStatus.processing
        job.started_at = datetime.now(timezone.utc)
        _log_activity(db, user_id=job.user_id, job_id=job.id, event_type="job_processing", message="Video generation started")
        db.commit()

        try:
            input_data = job.input_data or {}
            product_url = input_data.get("product_url", "")
            product_text = input_data.get("product_text", "")

            if product_url:
                product_info = scrape_product(product_url)
                product_text = product_text or product_info.get("title", "Amazing Product")
                images = product_info.get("images", [])
            else:
                images = []

            generator = VideoGeneratorService()
            video_path = generator.generate_promo_video(
                images=images,
                text=product_text or "Amazing Product",
                product_url=product_url,
            )

            file_size = os.path.getsize(video_path) if os.path.isfile(video_path) else 0

            asset = Asset(
                job_id=job.id,
                user_id=job.user_id,
                asset_type=AssetType.video,
                file_path=video_path,
                file_url=f"/media/{os.path.basename(video_path)}",
                file_size=file_size,
                duration=10.0,
                tags=["promo", "generated"],
            )
            db.add(asset)
            db.flush()

            scores = AnalysisService.score_content(
                transcript_text=product_text,
                duration=10.0,
                has_cta=bool(product_url),
            )
            explanation = AnalysisService.explain_scores(scores)
            recs = AnalysisService.platform_recommendations(scores, duration=10.0)

            analysis = Analysis(
                job_id=job.id,
                asset_id=asset.id,
                hook_score=scores["hook_score"],
                cta_score=scores["cta_score"],
                pacing_score=scores["pacing_score"],
                platform_fit_score=scores["platform_fit_score"],
                engagement_score=scores["engagement_score"],
                explanation=explanation,
                platform_recommendations=recs,
            )
            db.add(analysis)

            job.status = JobStatus.completed
            job.completed_at = datetime.now(timezone.utc)
            job.output_data = {
                "video_path": video_path,
                "scores": scores,
                "asset_id": str(asset.id),
            }

            _log_activity(db, user_id=job.user_id, job_id=job.id, event_type="job_completed", message="Video generation completed")
            db.commit()

            return {"status": "completed", "video_path": video_path, "scores": scores}

        except Exception as exc:
            logger.exception("Video generation failed for job %s", job_id)
            job.status = JobStatus.failed
            job.error_message = str(exc)
            job.completed_at = datetime.now(timezone.utc)
            _log_activity(db, user_id=job.user_id, job_id=job.id, event_type="job_failed", message=f"Video generation failed: {exc}", level=LogLevel.error)
            db.commit()
            raise self.retry(exc=exc, countdown=30)


@celery_app.task(name="app.workers.tasks.process_clip_shorts", bind=True, max_retries=2)
def process_clip_shorts(self, job_id: str) -> dict:
    job_uuid = uuid.UUID(job_id)

    with SyncSession() as db:
        job = db.execute(select(Job).where(Job.id == job_uuid)).scalar_one_or_none()
        if not job:
            logger.error("Job %s not found", job_id)
            return {"error": "Job not found"}

        job.status = JobStatus.processing
        job.started_at = datetime.now(timezone.utc)
        _log_activity(db, user_id=job.user_id, job_id=job.id, event_type="job_processing", message="Clip extraction started")
        db.commit()

        try:
            input_data = job.input_data or {}
            youtube_url = input_data.get("youtube_url", "")

            yt_service = YouTubeService()
            if youtube_url:
                video_path = yt_service.download_video(youtube_url)
            else:
                video_path = yt_service._create_mock(youtube_url)

            transcriber = TranscriptionService()
            transcript = transcriber.transcribe(video_path)

            extractor = ClipExtractorService()
            clips = extractor.extract_clips(video_path, transcript)

            asset_ids = []
            for i, clip in enumerate(clips):
                clip_path = clip.get("file_path", "")
                file_size = os.path.getsize(clip_path) if os.path.isfile(clip_path) else 0

                asset = Asset(
                    job_id=job.id,
                    user_id=job.user_id,
                    asset_type=AssetType.video,
                    file_path=clip_path,
                    file_url=f"/media/{os.path.basename(clip_path)}",
                    file_size=file_size,
                    duration=clip.get("duration", 30.0),
                    tags=["clip", "shorts", f"clip_{i+1}"],
                )
                asset.metadata_ = {"text": clip.get("text", ""), "start": clip.get("start"), "end": clip.get("end")}
                db.add(asset)
                db.flush()
                asset_ids.append(str(asset.id))

                scores = AnalysisService.score_content(
                    transcript_text=clip.get("text", ""),
                    duration=clip.get("duration", 30.0),
                )
                explanation = AnalysisService.explain_scores(scores)

                analysis = Analysis(
                    job_id=job.id,
                    asset_id=asset.id,
                    hook_score=scores["hook_score"],
                    cta_score=scores["cta_score"],
                    pacing_score=scores["pacing_score"],
                    platform_fit_score=scores["platform_fit_score"],
                    engagement_score=scores["engagement_score"],
                    explanation=explanation,
                    clip_selection_reason=f"Clip {i+1}: {clip.get('text', '')[:80]}",
                    platform_recommendations=AnalysisService.platform_recommendations(scores, clip.get("duration", 30.0)),
                )
                db.add(analysis)

            job.status = JobStatus.completed
            job.completed_at = datetime.now(timezone.utc)
            job.output_data = {
                "clips_count": len(clips),
                "asset_ids": asset_ids,
                "transcript_text": transcript.get("text", "")[:500],
            }

            _log_activity(db, user_id=job.user_id, job_id=job.id, event_type="job_completed", message=f"Extracted {len(clips)} clips")
            db.commit()

            return {"status": "completed", "clips_count": len(clips), "asset_ids": asset_ids}

        except Exception as exc:
            logger.exception("Clip extraction failed for job %s", job_id)
            job.status = JobStatus.failed
            job.error_message = str(exc)
            job.completed_at = datetime.now(timezone.utc)
            _log_activity(db, user_id=job.user_id, job_id=job.id, event_type="job_failed", message=f"Clip extraction failed: {exc}", level=LogLevel.error)
            db.commit()
            raise self.retry(exc=exc, countdown=30)
