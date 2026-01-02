"""
FastAPI server for TikTok video downloader.
Simplified version for PythonAnywhere free tier (no PostgreSQL, Redis, or Celery).
Downloads videos synchronously and uses background tasks for cleanup.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
import os
import tempfile
import urllib.parse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from downloaders.tiktok_downloader import TikTokDownloader
from schemas import DownloadRequest, DownloadResponse, HealthResponse

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="TikTok Downloader API", version="3.0.0")

# Enable CORS for Android app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key configuration
API_KEY = os.getenv("API_KEY", "your-secret-api-key-change-this")
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Initialize downloader with temp directory
downloader = TikTokDownloader(
    output_dir=os.path.join(tempfile.gettempdir(), "tiktok_downloads")
)

# Track files for cleanup: {file_path: created_at}
files_to_cleanup = {}


def verify_api_key(api_key: str = Depends(API_KEY_HEADER)) -> bool:
    """Verify API key."""
    if not API_KEY:
        return True  # No API key required if not set
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True


async def cleanup_file_after_delay(file_path: str):
    """
    Background task to delete a file after 1 hour.

    Args:
        file_path: Path to the file to delete
    """
    import asyncio

    # Wait 1 hour
    await asyncio.sleep(3600)  # 3600 seconds = 1 hour

    # Delete the file if it still exists
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up temporary file: {file_path}")
            # Remove from tracking
            files_to_cleanup.pop(file_path, None)
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {e}")


@app.get("/health", response_model=HealthResponse)
async def root():
    return HealthResponse(
        message="TikTok Downloader API",
        version="3.0.0",
        uses="Direct download (no database, no Celery)",
    )


@app.post(
    "/download", response_model=DownloadResponse, dependencies=[Depends(verify_api_key)]
)
async def download_video(
    request: DownloadRequest,
    background_tasks: BackgroundTasks,
):
    """
    Download a TikTok video from the given URL synchronously.
    Returns the file path immediately after download completes.

    Args:
        request: DownloadRequest containing the TikTok URL
        background_tasks: FastAPI background tasks for cleanup

    Returns:
        DownloadResponse with file_name and file_path
    """
    try:
        if not request.url or "tiktok.com" not in request.url.lower():
            raise HTTPException(status_code=400, detail="Invalid TikTok URL")

        # Download the video synchronously
        file_path = downloader.download(request.url)
        file_name = os.path.basename(file_path)

        # Track file for cleanup
        files_to_cleanup[file_path] = datetime.now()

        # Schedule cleanup after 1 hour
        background_tasks.add_task(cleanup_file_after_delay, file_path)

        return DownloadResponse(
            success=True,
            message="Download completed",
            file_name=file_name,
            file_path=file_path,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.get("/download/file/{file_name:path}")
async def get_downloaded_file(file_name: str, api_key: str = Depends(API_KEY_HEADER)):
    """
    Retrieve a downloaded video file.

    Args:
        file_name: Name of the file to retrieve (URL encoded if it contains special characters)
                   Can be just the filename or the full path

    Returns:
        FileResponse with the video file
    """
    # URL decode the filename in case it was encoded
    file_name = urllib.parse.unquote(file_name)

    # Check if it's a full path or just a filename
    if os.path.isabs(file_name) and os.path.exists(file_name):
        # It's a full path that exists
        file_path = file_name
    else:
        # It's just a filename, join with output directory
        file_path = os.path.join(downloader.output_dir, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_name}")

    # Get the actual filename for the response
    actual_filename = os.path.basename(file_path)

    return FileResponse(file_path, media_type="video/mp4", filename=actual_filename)


if __name__ == "__main__":
    import uvicorn
    import sys

    # Enable reload in development mode
    # Set RELOAD=true environment variable or pass --reload flag
    reload = os.getenv("RELOAD", "false").lower() == "true" or "--reload" in sys.argv

    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=reload)
