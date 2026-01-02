# TikTok Downloader

A Python-based TikTok video downloader with Android app support.

## Features

- Download TikTok videos by URL
- REST API server for remote access
- Android mobile app with APK support

## Setup

### Python Backend

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

   Note: Poetry is configured to create a `.venv` folder in the project directory for the virtual environment.

3. Run the API server:

**Standard mode:**
```bash
poetry run python api_server.py
```

**Development mode with auto-reload (recommended for development):**
```bash
# Option 1: Using uvicorn directly
poetry run uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Using environment variable
RELOAD=true poetry run python api_server.py

# Option 3: Using --reload flag
poetry run python api_server.py --reload
```

The server will run on `http://localhost:8000`

**Note:** With `--reload`, the server automatically restarts when you make code changes, which is perfect for development!

## API Endpoints

- `GET /` - API information
- `POST /download` - Download a TikTok video
  - Request body: `{"url": "https://www.tiktok.com/..."}`
  - Response: `{"success": true, "message": "...", "file_path": "..."}`
- `GET /download/file/{file_name}` - Retrieve downloaded video file

## Android App

The Android app is located in the `android_app/` directory.

### Building the APK

1. Open the project in Android Studio
2. Build > Build Bundle(s) / APK(s) > Build APK(s)
3. The APK will be generated in `android_app/app/build/outputs/apk/`

### Running the App

1. Start the Python API server (see Setup above)
2. Update the API URL in the Android app if needed (default: `http://10.0.2.2:8000` for emulator)
3. Install the APK on your Android device
4. Enter a TikTok URL and download

## Usage

### Python Class

```python
from downloaders.tiktok_downloader import TikTokDownloader

downloader = TikTokDownloader()
file_path = downloader.download("https://www.tiktok.com/@user/video/1234567890")
print(f"Downloaded to: {file_path}")
```

## Requirements

- Python 3.14+
- Poetry
- Android Studio (for building APK)

