# PythonAnywhere Limitations for TikTok Downloader

## The Problem

PythonAnywhere's **free tier blocks outbound connections** to most external websites. Only whitelisted domains are accessible, and `www.tiktok.com` is **not** on the whitelist.

### Error Messages You'll See:

1. **Connection Refused**:
   ```
   Failed to establish a new connection: [Errno 111] Connection refused
   ```

2. **Proxy Errors** (if proxy is configured):
   ```
   Unable to connect to proxy: Tunnel connection failed: 403 Forbidden
   ```

## Why This Happens

PythonAnywhere's free tier is designed for web apps that:
- Serve web pages
- Connect to whitelisted services (like databases, APIs)
- Don't need to make arbitrary outbound HTTP requests

TikTok video downloading requires:
- Making HTTP requests to `www.tiktok.com`
- Following redirects to CDN servers
- Downloading video files from various domains

These operations are **blocked** on the free tier.

## Solutions

### Option 1: Upgrade PythonAnywhere (Paid Plan)

**Cost**: ~$5/month (Hacker plan)

**Benefits**:
- Allows outbound connections to any domain
- Your current code will work without changes
- Keep using PythonAnywhere's simple deployment

**How to Upgrade**:
1. Go to PythonAnywhere Dashboard
2. Click "Upgrade" or "Account" → "Upgrade"
3. Choose "Hacker" plan ($5/month)
4. Your app will automatically get outbound connection access

### Option 2: Use a Different Free Hosting Provider

#### A. Railway (Recommended)

**Free Tier**: $5/month credit (enough for small apps)

**Setup**:
1. Sign up at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway auto-detects Flask apps
4. Add environment variables in Railway dashboard
5. Deploy!

**Pros**:
- Very easy deployment
- Free tier is generous
- No outbound connection restrictions
- Auto-deploys on git push

**Cons**:
- Free credit expires after inactivity
- Need to provide payment method (but won't charge if under limit)

#### B. Render

**Free Tier**: Free with limitations

**Setup**:
1. Sign up at [render.com](https://render.com)
2. Create new "Web Service"
3. Connect GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn api_server_flask:app`

**Pros**:
- Truly free tier
- No outbound restrictions
- Easy deployment

**Cons**:
- App sleeps after 15 minutes of inactivity (free tier)
- First request after sleep is slow (~30 seconds)

#### C. Fly.io

**Free Tier**: 3 shared VMs

**Setup**:
1. Sign up at [fly.io](https://fly.io)
2. Install flyctl CLI
3. Run: `fly launch` in your project directory
4. Follow prompts

**Pros**:
- Generous free tier
- No outbound restrictions
- Fast global deployment

**Cons**:
- Requires CLI setup
- More complex than Railway/Render

#### D. Heroku (Alternative)

**Note**: Heroku removed their free tier, but has a low-cost option

**Cost**: ~$5-7/month (Eco dyno)

**Pros**:
- Very reliable
- Easy deployment
- Well-documented

**Cons**:
- No longer free
- More expensive than other options

### Option 3: Use Your Own Server/VPS

If you have access to a VPS or can rent one:

**Providers**:
- DigitalOcean Droplets ($4-6/month)
- Linode ($5/month)
- Vultr ($2.50/month)
- AWS EC2 (free tier for 12 months, then pay-as-you-go)

**Setup**:
1. Deploy your Flask app
2. Use nginx as reverse proxy
3. Set up SSL with Let's Encrypt
4. No restrictions on outbound connections

## Recommended: Railway

For a quick, free solution, **Railway** is recommended:

1. **Sign up**: [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. **Select your repository**
4. **Add environment variables**:
   - `API_KEY=your-api-key-here`
5. **Deploy!**

Railway will:
- Auto-detect Flask
- Install dependencies
- Deploy your app
- Give you a URL like `your-app.railway.app`

## Migration Steps (PythonAnywhere → Railway)

1. **Export your code** (already in GitHub, right?)
2. **Sign up for Railway**
3. **Deploy from GitHub**
4. **Add environment variables** in Railway dashboard
5. **Update Android app** `BASE_URL` to Railway URL
6. **Test!**

## Testing Locally First

Before deploying anywhere, test that downloads work:

```bash
# On your local machine
cd tiktok_downloader_backend
python api_server_flask.py

# In another terminal
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"url": "https://www.tiktok.com/t/ZThJMSDvK/"}'
```

If this works locally but fails on PythonAnywhere, it confirms the outbound connection restriction.

## Summary

**PythonAnywhere Free Tier**: ❌ Blocks TikTok downloads  
**PythonAnywhere Paid**: ✅ Works, but costs $5/month  
**Railway Free Tier**: ✅ Works, free with credit  
**Render Free Tier**: ✅ Works, but sleeps after inactivity  
**Fly.io Free Tier**: ✅ Works, generous free tier  

**Recommendation**: Use **Railway** for the easiest free deployment that works with TikTok downloads.

