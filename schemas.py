"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel


class DownloadRequest(BaseModel):
    """Request schema for downloading a TikTok video."""

    url: str


class DownloadResponse(BaseModel):
    """Response schema for download completion."""

    success: bool
    message: str
    file_name: str | None = None
    file_path: str | None = None

    model_config = {
        "json_encoders": {str: str},
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Download completed",
                "file_name": "video.mp4",
                "file_path": "/tmp/tiktok_downloads/video.mp4",
            }
        },
    }
