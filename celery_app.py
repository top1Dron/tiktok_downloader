"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Redis URL for Celery broker and result backend - must be set in environment variables
REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise ValueError(
        "REDIS_URL environment variable is required. "
        "Set it in .env file or environment. "
        "Example: redis://localhost:6379/0"
    )

celery_app = Celery(
    "tiktok_downloader", broker=REDIS_URL, backend=REDIS_URL, include=["tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    # Periodic task schedule (Celery Beat)
    beat_schedule={
        "cleanup-old-files": {
            "task": "tasks.cleanup_old_files",
            "schedule": crontab(minute="*/15"),  # Run every 15 minutes
        },
    },
)
