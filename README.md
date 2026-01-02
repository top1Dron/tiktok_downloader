# TikTok Downloader Backend

A Python-based TikTok video downloader backend with REST API and WebSocket support.

## Features

- Download TikTok videos by URL
- REST API server for remote access
- WebSocket support for real-time updates
- Celery for background task processing
- PostgreSQL for task persistence
- Redis for message queuing and pub/sub

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
  - Headers: `X-API-Key: your-api-key` (if API_KEY is set)
  - Response: `{"success": true, "message": "...", "task_id": "..."}`
- `GET /download/status/{task_id}` - Get download task status
- `GET /download/file/{file_name}` - Retrieve downloaded video file
- `WS /ws/{client_id}` - WebSocket endpoint for real-time updates

## Environment Variables

See [ENV_SETUP.md](./ENV_SETUP.md) for detailed environment variable configuration.

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

Optional variables:
- `API_KEY` - API authentication key
- `RELOAD` - Enable auto-reload for development

## Docker Deployment

See [DOCKER.md](./DOCKER.md) for Docker and Docker Compose setup.

**Quick start:**
1. Copy `.env.example` to `.env` and configure
2. Run `docker-compose up -d`

## Usage

### Python Class

```python
from downloaders.tiktok_downloader import TikTokDownloader

downloader = TikTokDownloader()
file_path = downloader.download("https://www.tiktok.com/@user/video/1234567890")
print(f"Downloaded to: {file_path}")
```

## Deployment

- **Heroku**: See [HEROKU_DEPLOYMENT.md](./HEROKU_DEPLOYMENT.md) for deployment guide
- **Docker**: See [DOCKER.md](./DOCKER.md) for containerized deployment

## Requirements

- Python 3.11+
- Poetry
- PostgreSQL
- Redis

## Related Projects

- **Android App**: See `../tiktok_downloader_android_app/` for the mobile client

