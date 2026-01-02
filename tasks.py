"""Celery tasks for background processing."""

from celery_app import celery_app
from downloaders.tiktok_downloader import TikTokDownloader
import os
import tempfile
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, DownloadTask
import traceback
import json
import redis
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")


def get_downloader():
    """Get TikTok downloader instance."""
    output_dir = os.path.join(tempfile.gettempdir(), "tiktok_downloads")
    return TikTokDownloader(output_dir=output_dir)


def publish_task_update(task_id: str, task: DownloadTask):
    """Publish task update to Redis pub/sub for WebSocket notifications."""
    try:
        redis_client = redis.from_url(REDIS_URL)
        message = json.dumps(
            {
                "task_id": task_id,
                "status": task.status,
                "file_path": task.file_path,
                "file_name": task.file_name,
                "error": task.error,
                "url": task.url,
            }
        )
        redis_client.publish("task_updates", message)
    except Exception as e:
        # Don't fail the task if Redis publish fails
        print(f"Failed to publish task update to Redis: {e}")


@celery_app.task(bind=True, name="tasks.download_video")
def download_video_task(self, task_id: str, url: str):
    """
    Celery task to download TikTok video.

    Args:
        task_id: Unique task identifier
        url: TikTok video URL
    """
    db: Session = SessionLocal()

    try:
        # Update status to downloading
        task = db.query(DownloadTask).filter(DownloadTask.task_id == task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found in database")

        task.status = "downloading"
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)

        # Notify WebSocket clients via Redis
        publish_task_update(task_id, task)

        # Download the video
        downloader = get_downloader()
        file_path = downloader.download(url)
        file_name = os.path.basename(file_path)

        # Update task status to completed
        task.status = "completed"
        task.file_path = file_path
        task.file_name = file_name
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)

        # Notify WebSocket clients via Redis
        publish_task_update(task_id, task)

        return {
            "task_id": task_id,
            "status": "completed",
            "file_path": file_path,
            "file_name": file_name,
        }

    except Exception as e:
        # Update task status to failed
        error_msg = str(e)

        task = db.query(DownloadTask).filter(DownloadTask.task_id == task_id).first()
        if task:
            task.status = "failed"
            task.error = error_msg
            task.completed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(task)

            # Notify WebSocket clients via Redis
            publish_task_update(task_id, task)

        # Don't retry, just fail
        raise

    finally:
        db.close()


@celery_app.task(name="tasks.cleanup_old_files")
def cleanup_old_files():
    """
    Periodic task to delete temporary files that are older than 1 hour.
    Runs every 15 minutes to check for files that need to be deleted.
    """
    db: Session = SessionLocal()
    deleted_count = 0
    error_count = 0

    try:
        # Calculate the cutoff time (1 hour ago)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)

        # Find all completed tasks that were completed more than 1 hour ago
        old_tasks = (
            db.query(DownloadTask)
            .filter(
                DownloadTask.status == "completed",
                DownloadTask.completed_at.isnot(None),
                DownloadTask.completed_at < cutoff_time,
                DownloadTask.file_path.isnot(None),
            )
            .all()
        )

        for task in old_tasks:
            try:
                file_path = task.file_path

                # Check if file exists and delete it
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
                    print(
                        f"Deleted old file: {file_path} (completed at {task.completed_at})"
                    )

                    # Optionally, clear the file_path in database to indicate it's been deleted
                    # task.file_path = None
                    # db.commit()

            except Exception as e:
                error_count += 1
                print(f"Error deleting file {task.file_path}: {e}")

        db.commit()

        if deleted_count > 0 or error_count > 0:
            print(
                f"Cleanup completed: {deleted_count} files deleted, {error_count} errors"
            )

        return {
            "deleted_count": deleted_count,
            "error_count": error_count,
            "checked_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        print(f"Error in cleanup_old_files task: {e}")
        traceback.print_exc()
        return {
            "deleted_count": deleted_count,
            "error_count": error_count,
            "error": str(e),
        }
    finally:
        db.close()
