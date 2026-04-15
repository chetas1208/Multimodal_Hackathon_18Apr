from __future__ import annotations

from celery import Celery

from app.config import settings

celery_app = Celery(
    "marketing_studio",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=86400,
    task_routes={
        "app.workers.tasks.process_generate_video": {"queue": "video"},
        "app.workers.tasks.process_clip_shorts": {"queue": "clips"},
    },
)

celery_app.autodiscover_tasks(["app.workers"])
