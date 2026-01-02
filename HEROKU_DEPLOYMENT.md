# Heroku Deployment Guide for TikTok Downloader Backend

This guide will help you deploy the TikTok Downloader backend to Heroku's free plan.

## ⚠️ Important Notes for Heroku Free Plan

1. **Dyno Sleeping**: Free dynos sleep after 30 minutes of inactivity. The first request after sleeping may take 10-30 seconds to respond.
2. **Monthly Hours**: Free plan includes 550-1000 hours/month. You'll need 2 dynos (web + worker), so you have ~275-500 hours each.
3. **Ephemeral Filesystem**: Files stored in `/tmp` are deleted when the dyno restarts. Downloaded videos will be lost.
4. **Database & Redis**: Use Heroku addons (free tiers available).

## Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://www.heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Your project should be in a Git repository

## Step 1: Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

## Step 2: Login to Heroku

```bash
heroku login
```

This will open a browser window for authentication.

## Step 3: Create Heroku App

```bash
cd /Users/apple/Desktop/work/test/tiktok_downloader/tiktok_downloader_backend
heroku create your-app-name
```

Replace `your-app-name` with your desired app name (must be unique). If you don't specify a name, Heroku will generate one.

## Step 4: Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:mini
```

The `mini` plan is free and includes:
- 10,000 rows
- 20 connections
- 1 GB storage

## Step 5: Add Redis

```bash
heroku addons:create heroku-redis:mini
```

The `mini` plan is free and includes:
- 25 MB memory
- 20 connections

## Step 6: Configure Environment Variables

Set your environment variables on Heroku:

```bash
# Set API key (change this to a secure random string)
heroku config:set API_KEY=your-secret-api-key-change-this

# Database URL is automatically set by Heroku Postgres addon
# Redis URL is automatically set by Heroku Redis addon
# You can verify with:
heroku config
```

The `DATABASE_URL` and `REDIS_URL` are automatically set by Heroku addons, so you don't need to set them manually.

## Step 7: Prepare Your Code

### 7.1 Update Database URL Handling

Heroku's PostgreSQL uses `postgres://` instead of `postgresql://`. Update `database.py` to handle both:

```python
# In database.py, after getting DATABASE_URL:
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
```

### 7.2 Update Redis URL Handling

Heroku Redis may use `rediss://` (SSL) or `redis://`. Your code should handle both.

### 7.3 Ensure Files Are Committed

```bash
git add .
git commit -m "Prepare for Heroku deployment"
```

## Step 8: Deploy to Heroku

```bash
# Push to Heroku (this will trigger a build)
git push heroku main

# If your default branch is 'master':
git push heroku master
```

Heroku will:
1. Detect Python from `requirements.txt`
2. Install dependencies
3. Run database migrations (if configured)
4. Start your dynos

## Step 9: Run Database Migrations

```bash
# Run Alembic migrations
heroku run alembic upgrade head
```

Or if you need to create tables manually:

```bash
heroku run python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

## Step 10: Scale Dynos

Start both web and worker dynos:

```bash
# Start web dyno (API server)
heroku ps:scale web=1

# Start worker dyno (Celery worker)
heroku ps:scale worker=1
```

## Step 11: Verify Deployment

```bash
# Check dyno status
heroku ps

# View logs
heroku logs --tail

# Test the API
curl https://your-app-name.herokuapp.com/
```

## Step 12: Update Android App Configuration

Update your Android app's `BASE_URL` to point to your Heroku app:

```kotlin
// In ApiService.kt or your config
const val BASE_URL = "https://your-app-name.herokuapp.com"
```

## Monitoring and Maintenance

### View Logs

```bash
# Real-time logs
heroku logs --tail

# Web dyno logs only
heroku logs --tail --dyno web

# Worker dyno logs only
heroku logs --tail --dyno worker
```

### Check Dyno Status

```bash
heroku ps
```

### Restart Dynos

```bash
# Restart all dynos
heroku restart

# Restart specific dyno
heroku restart web
heroku restart worker
```

### Access Database

```bash
# Open PostgreSQL console
heroku pg:psql
```

### Access Redis

```bash
# Open Redis console
heroku redis:cli
```

## Troubleshooting

### Issue: App crashes on startup

**Check logs:**
```bash
heroku logs --tail
```

**Common causes:**
- Missing environment variables
- Database connection issues
- Redis connection issues

### Issue: Worker not processing tasks

**Check worker logs:**
```bash
heroku logs --tail --dyno worker
```

**Verify worker is running:**
```bash
heroku ps
```

### Issue: Files not persisting

**Note**: Heroku's filesystem is ephemeral. Files in `/tmp` are deleted when dynos restart. Consider:
- Using external storage (AWS S3, Google Cloud Storage)
- Serving files immediately after download
- Not storing files long-term on Heroku

### Issue: Dyno sleeping

Free dynos sleep after 30 minutes. Solutions:
- Upgrade to a paid plan
- Use a service like [Kaffeine](https://kaffeine.herokuapp.com/) to ping your app
- Accept the cold start delay

### Issue: Out of hours

Free plan has limited hours. Check usage:
```bash
heroku ps:type
```

## Cost Optimization Tips

1. **Use Free Hours Wisely**: Free plan includes 550-1000 hours/month. With 2 dynos, you get ~275-500 hours each.
2. **Scale Down When Not Needed**: 
   ```bash
   heroku ps:scale worker=0  # Stop worker when not needed
   ```
3. **Monitor Usage**: Check your Heroku dashboard regularly.

## Upgrading from Free Plan

If you need:
- **No sleeping dynos**: Upgrade to Hobby ($7/month per dyno)
- **More database storage**: Upgrade PostgreSQL plan
- **More Redis memory**: Upgrade Redis plan
- **More hours**: Upgrade to Standard dynos

## Environment Variables Reference

| Variable | Description | Required | Auto-set by Heroku |
|----------|-------------|----------|-------------------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | ✅ (Postgres addon) |
| `REDIS_URL` | Redis connection string | Yes | ✅ (Redis addon) |
| `API_KEY` | API authentication key | No | ❌ (set manually) |
| `PORT` | Port to bind to | Yes | ✅ (Heroku sets this) |

## File Structure for Heroku

Your project should have:
```
tiktok_downloader_backend/
├── Procfile          # Process definitions
├── requirements.txt  # Python dependencies
├── runtime.txt       # Python version
├── api_server.py     # Main API server
├── celery_app.py     # Celery configuration
├── tasks.py          # Celery tasks
├── database.py       # Database models
└── ...              # Other files
```

## Quick Deploy Checklist

- [ ] Heroku CLI installed and logged in
- [ ] Git repository initialized
- [ ] Heroku app created
- [ ] PostgreSQL addon added
- [ ] Redis addon added
- [ ] Environment variables set
- [ ] Code committed to Git
- [ ] Pushed to Heroku
- [ ] Database migrations run
- [ ] Dynos scaled (web=1, worker=1)
- [ ] App tested and working
- [ ] Android app updated with new URL

## Next Steps

1. **Set up custom domain** (optional, requires paid plan)
2. **Enable SSL** (automatic on Heroku)
3. **Set up monitoring** (Heroku Metrics, Logentries)
4. **Configure backups** (Heroku Postgres backups)

## Support

- [Heroku Documentation](https://devcenter.heroku.com/)
- [Heroku Support](https://help.heroku.com/)
- [Heroku Status](https://status.heroku.com/)

---

**Note**: Heroku's free plan is great for development and testing, but for production use, consider upgrading to a paid plan for better reliability and performance.

