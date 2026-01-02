# Docker Deployment Guide

## Quick Start

1. **Set your API key** in `docker-compose.yml` or create a `.env` file:
   ```bash
   API_KEY=your-secret-api-key-here
   ```

2. **Build and run**:
   ```bash
   cd backend
   docker-compose up -d
   ```

3. **Check logs**:
   ```bash
   docker-compose logs -f
   ```

## Environment Variables

- `API_KEY`: Secret API key for authentication (required)
- `RELOAD`: Set to `true` for development auto-reload (default: false)

## Building the Image

```bash
docker build -t tiktok-downloader-api .
```

## Running the Container

```bash
docker run -d \
  -p 8000:8000 \
  -e API_KEY=your-secret-api-key \
  -v $(pwd)/downloads:/app/downloads \
  tiktok-downloader-api
```

## Docker Compose

The `docker-compose.yml` file includes:
- API service on port 8000
- Volume mounts for downloads
- Health checks
- Auto-restart on failure

## Production Deployment

For production, make sure to:
1. Set a strong `API_KEY`
2. Use HTTPS (add nginx/traefik reverse proxy)
3. Set up proper logging
4. Configure resource limits
5. Use secrets management for API keys

