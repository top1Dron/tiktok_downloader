# Environment Variables Setup

## Using .env File (Recommended)

1. **Create a `.env` file** in the `backend/` directory:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env` file** and set your configuration:
   ```env
   API_KEY=your-secret-api-key-change-this
   DATABASE_URL=postgresql://tiktok_user:tiktok_pass@localhost:5432/tiktok_downloader
   REDIS_URL=redis://localhost:6379/0
   RELOAD=false
   ```
   
   **Important:** `DATABASE_URL` and `REDIS_URL` are now **required** environment variables.

3. **Install dependencies** (if not already done):
   ```bash
   poetry install
   ```

4. **Run the server**:
   ```bash
   poetry run python api_server.py
   ```

The `.env` file will be automatically loaded when the server starts.

## Using Environment Variables Directly

Alternatively, you can set environment variables directly:

### Linux/Mac:
```bash
export API_KEY=your-secret-api-key-change-this
export RELOAD=false
poetry run python api_server.py
```

### Windows (PowerShell):
```powershell
$env:API_KEY="your-secret-api-key-change-this"
$env:RELOAD="false"
poetry run python api_server.py
```

### Windows (CMD):
```cmd
set API_KEY=your-secret-api-key-change-this
set RELOAD=false
poetry run python api_server.py
```

## Docker/Docker Compose

For Docker deployments, set the API key in `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      - API_KEY=${API_KEY:-your-secret-api-key-change-this}
```

Or create a `.env` file in the same directory as `docker-compose.yml`:
```env
API_KEY=your-secret-api-key-change-this
```

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to version control (it's in `.gitignore`)
- Use a strong, random API key in production
- The `.env.example` file is safe to commit (it contains placeholder values)

## Available Environment Variables

- `API_KEY` - Secret key for API authentication (required)
- `DATABASE_URL` - PostgreSQL connection string (required)
  - Format: `postgresql://username:password@host:port/database_name`
  - Example: `postgresql://tiktok_user:tiktok_pass@localhost:5432/tiktok_downloader`
- `REDIS_URL` - Redis connection string for Celery (required)
  - Format: `redis://host:port/db_number`
  - Example: `redis://localhost:6379/0`
- `RELOAD` - Enable auto-reload for development (`true`/`false`, default: `false`)
- `HOST` - Server host (optional, default: `0.0.0.0`)
- `PORT` - Server port (optional, default: `8000`)

