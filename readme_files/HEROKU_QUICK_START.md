# Heroku Quick Start Guide

## Prerequisites
- Heroku account: [heroku.com](https://www.heroku.com)
- Heroku CLI installed: `brew install heroku` (macOS)
- Git repository initialized

## Quick Deploy (5 minutes)

```bash
# 1. Login
heroku login

# 2. Create app
cd /Users/apple/Desktop/work/test/tiktok_downloader/tiktok_downloader_backend
heroku create your-app-name

# 3. Add database and Redis (free tier)
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini

# 4. Set API key
heroku config:set API_KEY=your-secret-api-key-change-this

# 5. Generate requirements.txt from Poetry (required for Heroku)
./bash_scripts/generate_requirements.sh

# 6. Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# 7. Setup database
heroku run python -c "from config.database import Base, engine; Base.metadata.create_all(bind=engine)"

# 8. Start dynos
heroku ps:scale web=1 worker=1

# 9. Test
curl https://your-app-name.herokuapp.com/
```

## Your App URL
```
https://your-app-name.herokuapp.com
```

## Important Notes

⚠️ **Free Plan Limitations:**
- Dynos sleep after 30 min inactivity (first request may be slow)
- ~275-500 hours/month per dyno (you have 2: web + worker)
- Files in `/tmp` are deleted on restart (ephemeral filesystem)

## View Logs
```bash
heroku logs --tail
```

## Stop Worker (Save Hours)
```bash
heroku ps:scale worker=0
```

## Restart App
```bash
heroku restart
```

## Full Guide
See [HEROKU_DEPLOYMENT.md](./HEROKU_DEPLOYMENT.md) for detailed instructions.

