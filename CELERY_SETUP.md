# Celery + PostgreSQL Setup Guide

## Overview

The application now uses:
- **Celery** for background task processing (instead of FastAPI BackgroundTasks)
- **PostgreSQL** for persistent task storage (instead of in-memory dictionary)
- **Redis** as the message broker for Celery

## Prerequisites

1. PostgreSQL 16+ (or use Docker)
2. Redis 7+ (or use Docker)
3. Python 3.14+

## Local Development Setup

### 1. Install Dependencies

```bash
cd backend
poetry install
```

### 2. Set Up Environment Variables

Create a `.env` file:

```env
API_KEY=your-secret-api-key-change-this
DATABASE_URL=postgresql://tiktok_user:tiktok_pass@localhost:5432/tiktok_downloader
REDIS_URL=redis://localhost:6379/0
```

### 3. Start PostgreSQL and Redis

**Using Docker Compose (Recommended):**
```bash
docker-compose up -d postgres redis
```

**Or manually:**
- Start PostgreSQL on port 5432
- Start Redis on port 6379

### 4. Initialize Database

```bash
# Create tables (using SQLAlchemy)
poetry run python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# Or use Alembic migrations
poetry run alembic upgrade head
```

### 5. Start the Services

**Terminal 1 - API Server:**
```bash
poetry run python api_server.py
```

**Terminal 2 - Celery Worker:**
```bash
poetry run celery -A celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (for periodic tasks like file cleanup):**
```bash
poetry run celery -A celery_app beat --loglevel=info
```

**Note:** Celery Beat is required for automatic cleanup of old temporary files. It runs the cleanup task every 15 minutes to delete files older than 1 hour.

## Docker Deployment

### Quick Start

```bash
cd backend
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis broker
- FastAPI server
- Celery worker
- Celery Beat (for periodic cleanup tasks)

### Check Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f celery
docker-compose logs -f celery-beat
```

## Database Migrations

### Create a Migration

```bash
poetry run alembic revision --autogenerate -m "description"
```

### Apply Migrations

```bash
poetry run alembic upgrade head
```

### Rollback

```bash
poetry run alembic downgrade -1
```

## Monitoring Celery

### Celery Flower (Optional)

Add to `docker-compose.yml`:

```yaml
flower:
  build:
    context: .
    dockerfile: Dockerfile
  command: celery -A celery_app flower --port=5555
  ports:
    - "5555:5555"
  environment:
    - CELERY_BROKER_URL=redis://redis:6379/0
  depends_on:
    - redis
```

Access at: http://localhost:5555

## Automatic File Cleanup

The system includes an automatic cleanup task that deletes temporary video files 1 hour after they were downloaded. This helps manage disk space on the server.

### How It Works

- **Cleanup Task**: `tasks.cleanup_old_files`
- **Schedule**: Runs every 15 minutes (via Celery Beat)
- **Deletion Criteria**: Files from completed downloads that are older than 1 hour
- **Safety**: Only deletes files that:
  - Have status "completed"
  - Have a `completed_at` timestamp older than 1 hour
  - Have a valid `file_path`

### Manual Cleanup

You can also trigger cleanup manually:

```bash
# Using Celery CLI
poetry run celery -A celery_app call tasks.cleanup_old_files

# Or using Python
poetry run python -c "from tasks import cleanup_old_files; cleanup_old_files()"
```

### Monitoring Cleanup

Check the Celery Beat logs to see cleanup activity:

```bash
# Local
poetry run celery -A celery_app beat --loglevel=info

# Docker
docker-compose logs -f celery-beat
```

You'll see messages like:
```
Deleted old file: /tmp/tiktok_downloads/video.mp4 (completed at 2024-01-15 10:00:00)
Cleanup completed: 5 files deleted, 0 errors
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Secret API key for authentication | `your-secret-api-key-change-this` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://tiktok_user:tiktok_pass@localhost:5432/tiktok_downloader` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `RELOAD` | Enable auto-reload for development | `false` |

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
psql -h localhost -U tiktok_user -d tiktok_downloader
```

### Redis Connection Issues

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli ping
```

### Celery Worker Not Processing Tasks

1. Check worker logs: `docker-compose logs celery`
2. Verify Redis connection
3. Verify database connection
4. Check task is registered: `celery -A celery_app inspect registered`

## Production Considerations

1. **Use strong API keys** - Generate secure random keys
2. **Database backups** - Set up regular PostgreSQL backups
3. **Redis persistence** - Configure Redis persistence
4. **Resource limits** - Set appropriate CPU/memory limits in Docker
5. **Monitoring** - Set up monitoring for Celery tasks
6. **Scaling** - Run multiple Celery workers for high load

