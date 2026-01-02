"""
FastAPI server for TikTok video downloader.
This server exposes the TikTokDownloader functionality via REST API.
Uses Celery for background tasks and PostgreSQL for persistence.
"""

from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
import os
import tempfile
import urllib.parse
import uuid
from datetime import datetime
import json
from typing import Dict
import asyncio
import redis
import threading
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Global event loop reference for thread-safe coroutine execution
app_event_loop = None
from config.database import get_db, DownloadTask, Base, engine
from tasks import download_video_task
from config.celery_app import celery_app
from downloaders.tiktok_downloader import TikTokDownloader
from schemas import DownloadRequest, DownloadResponse, DownloadStatus

# Load environment variables from .env file
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Redis URL for pub/sub
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Store WebSocket connections
websocket_connections: Dict[str, WebSocket] = {}

# Redis subscriber thread
redis_thread = None
# Global event loop reference for thread-safe coroutine execution
app_event_loop = None


def redis_subscriber_thread():
    """Background thread to subscribe to Redis and forward messages to WebSocket clients."""
    global app_event_loop
    try:
        redis_client = redis.from_url(REDIS_URL)
        pubsub = redis_client.pubsub()
        pubsub.subscribe("task_updates")

        for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")

                # Schedule coroutine to send to websockets
                if app_event_loop and app_event_loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        notify_websockets_from_redis(data), app_event_loop
                    )
    except Exception as e:
        print(f"Redis subscriber failed: {e}")


async def notify_websockets_from_redis(message_data: str):
    """Notify all WebSocket connections with message from Redis."""
    disconnected = []
    for client_id, websocket in websocket_connections.items():
        try:
            await websocket.send_text(message_data)
        except:
            disconnected.append(client_id)

    # Remove disconnected clients
    for client_id in disconnected:
        websocket_connections.pop(client_id, None)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - start and stop background tasks."""
    # Startup
    global redis_thread, app_event_loop
    app_event_loop = asyncio.get_event_loop()
    redis_thread = threading.Thread(target=redis_subscriber_thread, daemon=True)
    redis_thread.start()
    yield
    # Shutdown - thread will stop when daemon process exits


app = FastAPI(title="TikTok Downloader API", lifespan=lifespan)

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


def verify_api_key(api_key: str = Depends(API_KEY_HEADER)) -> bool:
    """Verify API key."""
    if not API_KEY:
        return True  # No API key required if not set
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True


async def notify_websockets(task_id: str, task: DownloadTask):
    """Notify all WebSocket connections about task update."""
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

    # Send to all connected clients
    disconnected = []
    for client_id, websocket in websocket_connections.items():
        try:
            await websocket.send_text(message)
        except:
            disconnected.append(client_id)

    # Remove disconnected clients
    for client_id in disconnected:
        websocket_connections.pop(client_id, None)


@app.get("/")
async def root():
    return {
        "message": "TikTok Downloader API",
        "version": "2.0.0",
        "uses": "Celery + PostgreSQL",
    }


@app.post(
    "/download", response_model=DownloadResponse, dependencies=[Depends(verify_api_key)]
)
async def download_video(request: DownloadRequest, db: Session = Depends(get_db)):
    """
    Start downloading a TikTok video from the given URL.
    Returns immediately with a task_id. Use WebSocket or status endpoint to check progress.

    Args:
        request: DownloadRequest containing the TikTok URL

    Returns:
        DownloadResponse with task_id
    """
    try:
        if not request.url or "tiktok.com" not in request.url.lower():
            raise HTTPException(status_code=400, detail="Invalid TikTok URL")

        # Create task in database
        task_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Start Celery task
        celery_result = download_video_task.delay(task_id, request.url)

        # Create database record
        db_task = DownloadTask(
            task_id=task_id,
            celery_task_id=celery_result.id,
            url=request.url,
            status="pending",
            created_at=now,
            updated_at=now,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)

        return DownloadResponse(
            success=True,
            message="Download started",
            task_id=task_id,
            celery_task_id=celery_result.id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.get("/download/status/{task_id}", response_model=DownloadStatus)
async def get_download_status(
    task_id: str,
    api_key: str = Depends(API_KEY_HEADER),
    db: Session = Depends(get_db),
):
    """Get the status of a download task."""
    task = db.query(DownloadTask).filter(DownloadTask.task_id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check Celery task status if available
    celery_status = None
    if task.celery_task_id:
        celery_result = celery_app.AsyncResult(task.celery_task_id)
        celery_status = celery_result.state

    return DownloadStatus(
        task_id=task.task_id,
        celery_task_id=task.celery_task_id,
        status=task.status,
        url=task.url,
        file_path=task.file_path,
        file_name=task.file_name,
        error=task.error,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time download updates."""
    await websocket.accept()
    websocket_connections[client_id] = websocket

    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            await websocket.send_text(
                json.dumps({"type": "pong", "client_id": client_id})
            )
    except WebSocketDisconnect:
        websocket_connections.pop(client_id, None)


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
