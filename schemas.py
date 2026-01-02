"""Pydantic schemas for API request/response models."""
from pydantic import BaseModel


class DownloadRequest(BaseModel):
    """Request schema for downloading a TikTok video."""
    url: str


class DownloadResponse(BaseModel):
    """Response schema for download initiation."""
    success: bool
    message: str
    task_id: str | None = None
    celery_task_id: str | None = None

    model_config = {
        "json_encoders": {str: str},
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Download started",
                "task_id": "uuid-here",
                "celery_task_id": "celery-task-id",
            }
        },
    }


class DownloadStatus(BaseModel):
    """Response schema for download task status."""
    task_id: str
    celery_task_id: str | None = None
    status: str  # "pending", "downloading", "completed", "failed"
    url: str
    file_path: str | None = None
    file_name: str | None = None
    error: str | None = None
    created_at: str
    updated_at: str
    completed_at: str | None = None

