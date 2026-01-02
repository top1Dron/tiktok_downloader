"""
Flask server for TikTok video downloader.
Simplified version for PythonAnywhere free tier (no PostgreSQL, Redis, or Celery).
Downloads videos synchronously and uses background tasks for cleanup.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
from downloaders.tiktok_downloader import TikTokDownloader
import threading
import time

# Load environment variables from .env file
# Try multiple possible locations for PythonAnywhere compatibility
env_loaded = False
possible_env_paths = [
    os.path.join(os.path.dirname(__file__), ".env"),  # Same directory as this file
    os.path.join(os.path.expanduser("~"), ".env"),  # Home directory
    os.path.join(
        os.path.expanduser("~"), "tiktok_downloader_backend", ".env"
    ),  # Project directory in home
    ".env",  # Current working directory
]

for env_path in possible_env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        env_loaded = True
        print(f"✅ Loaded .env file from: {env_path}")
        break

if not env_loaded:
    # Try default load_dotenv() as fallback
    load_dotenv()
    print("⚠️ Using default load_dotenv() - .env file may not be found")

app = Flask(__name__)

# Enable CORS for Android app
CORS(app)

# API Key configuration
API_KEY = os.getenv("API_KEY", "your-secret-api-key-change-this")

# Debug: Log API key status (without exposing the full key)
if API_KEY and API_KEY != "your-secret-api-key-change-this":
    print(f"✅ API_KEY loaded: ***{API_KEY[-4:] if len(API_KEY) > 4 else '****'}")
else:
    print("⚠️ WARNING: API_KEY not set or using default value!")
    print("   Set API_KEY in .env file or environment variable")

# Initialize downloader with temp directory
downloader = TikTokDownloader(
    output_dir=os.path.join(tempfile.gettempdir(), "tiktok_downloads")
)

# Track files for cleanup: {file_path: created_at}
files_to_cleanup = {}


def verify_api_key():
    """Verify API key from request headers."""
    if not API_KEY:
        return None  # No API key required if not set

    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        return jsonify({"detail": "Invalid API Key"}), 401
    return None


def cleanup_file_after_delay(file_path: str):
    """
    Background task to delete a file after 1 hour.

    Args:
        file_path: Path to the file to delete
    """
    # Wait 1 hour
    time.sleep(3600)  # 3600 seconds = 1 hour

    # Delete the file if it still exists
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up temporary file: {file_path}")
            # Remove from tracking
            files_to_cleanup.pop(file_path, None)
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {e}")


@app.route("/", methods=["GET"])
def root():
    return jsonify(
        {
            "message": "TikTok Downloader API",
            "version": "3.0.0",
            "uses": "Direct download (no database, no Celery)",
        }
    )


@app.route("/debug/config", methods=["GET"])
def debug_config():
    """
    Debug endpoint to check if API_KEY is loaded correctly.
    Only shows last 4 characters of API_KEY for security.
    """
    api_key_status = (
        "not set"
        if not API_KEY or API_KEY == "your-secret-api-key-change-this"
        else f"set (ends with: ...{API_KEY[-4:]})"
    )
    return jsonify(
        {
            "api_key_status": api_key_status,
            "api_key_required": API_KEY
            and API_KEY != "your-secret-api-key-change-this",
            "env_file_checked": True,
        }
    )


@app.route("/download", methods=["POST"])
def download_video():
    """
    Download a TikTok video from the given URL synchronously.
    Returns the file path immediately after download completes.

    Expected JSON body:
    {
        "url": "https://www.tiktok.com/t/..."
    }

    Returns:
        JSON response with file_name and file_path
    """
    # Verify API key
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"detail": "Missing 'url' in request body"}), 400

        url = data["url"]

        if not url or "tiktok.com" not in url.lower():
            return jsonify({"detail": "Invalid TikTok URL"}), 400

        # Download the video synchronously
        file_path = downloader.download(url)
        file_name = os.path.basename(file_path)

        # Track file for cleanup
        files_to_cleanup[file_path] = datetime.now()

        # Schedule cleanup after 1 hour in background thread
        cleanup_thread = threading.Thread(
            target=cleanup_file_after_delay, args=(file_path,)
        )
        cleanup_thread.daemon = True
        cleanup_thread.start()

        return jsonify(
            {
                "success": True,
                "message": "Download completed",
                "file_name": file_name,
                "file_path": file_path,
            }
        )
    except Exception as e:
        return jsonify({"detail": f"Download failed: {str(e)}"}), 500


@app.route("/download/file/<path:file_name>", methods=["GET"])
def get_downloaded_file(file_name: str):
    """
    Retrieve a downloaded video file.

    Args:
        file_name: Name of the file to retrieve (URL encoded if it contains special characters)
                   Can be just the filename or the full path

    Returns:
        File response with the video file
    """
    # Verify API key
    auth_error = verify_api_key()
    if auth_error:
        return auth_error

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
        return jsonify({"detail": f"File not found: {file_name}"}), 404

    # Get the actual filename for the response
    actual_filename = os.path.basename(file_path)

    return send_file(
        file_path,
        mimetype="video/mp4",
        as_attachment=True,
        download_name=actual_filename,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
