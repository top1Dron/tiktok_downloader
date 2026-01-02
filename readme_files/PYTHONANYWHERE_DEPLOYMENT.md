# Deploying to PythonAnywhere

This guide explains how to deploy the TikTok Downloader backend to PythonAnywhere's free tier.

## Prerequisites

1. A PythonAnywhere account (free tier available)
2. Your code pushed to a Git repository (GitHub, GitLab, etc.)

## Important Notes

- PythonAnywhere free tier supports Python 3.13
- The app uses WSGI wrapper (`wsgi.py`) to run FastAPI
- No database, Redis, or Celery required (simplified version)
- Files are stored temporarily and cleaned up after 1 hour

## Step 1: Upload Your Code

### Option A: Using Git (Recommended)

1. In PythonAnywhere Dashboard, go to **Files** tab
2. Open a Bash console
3. Clone your repository:
   ```bash
   cd ~
   git clone https://github.com/yourusername/tiktok_downloader_backend.git
   cd tiktok_downloader_backend
   ```

### Option B: Using Files Tab

1. Go to **Files** tab in PythonAnywhere
2. Navigate to your home directory
3. Upload all project files

## Step 2: Install Dependencies

1. Open a Bash console
2. Navigate to your project directory:
   ```bash
   cd ~/tiktok_downloader_backend
   ```
3. Create a virtual environment (if not exists):
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Step 3: Set Up Environment Variables

1. In PythonAnywhere Dashboard, go to **Files** tab
2. Navigate to your project directory
3. Create a `.env` file:
   ```bash
   nano .env
   ```
4. Add your configuration:
   ```env
   API_KEY=your-secret-api-key-here
   ```
5. Save and exit (Ctrl+X, then Y, then Enter)

## Step 4: Configure Web App

1. Go to **Web** tab in PythonAnywhere Dashboard
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.13**
5. Click **Next**

## Step 5: Set Up WSGI Configuration

**Important:** PythonAnywhere's WSGI file is different from your project's `wsgi.py` file!

1. In the **Web** tab, find **WSGI configuration file** link
   - It will be something like `/var/www/yourusername_pythonanywhere_com_wsgi.py`
   - This is NOT the `wsgi.py` file in your project folder!
2. Click it to edit the WSGI file
3. **Delete all the Django-related code** (PythonAnywhere's template is for Django by default)
4. Replace the entire content with this FastAPI configuration:
   ```python
   import sys
   import os

   # Add your project directory to the path
   # Replace 'yourusername' with your PythonAnywhere username
   project_home = '/home/yourusername/tiktok_downloader_backend'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)

   # Activate virtual environment
   activate_this = os.path.join(project_home, 'venv/bin/activate_this.py')
   if os.path.exists(activate_this):
       with open(activate_this) as file_:
           exec(file_.read(), dict(__file__=activate_this))

   # Import the WSGI application from your project's wsgi.py file
   from wsgi import application
   ```
5. **Important:** Replace `yourusername` with your actual PythonAnywhere username
   - Your username is in your PythonAnywhere URL: `https://yourusername.pythonanywhere.com`
6. Save the file

**Note:** See `readme_files/PYTHONANYWHERE_WSGI_EXAMPLE.py` for a complete example file.

## Step 6: Configure Static Files (Optional)

If you need to serve static files:

1. In **Web** tab, scroll to **Static files** section
2. Add a mapping:
   - **URL**: `/static/`
   - **Directory**: `/home/yourusername/tiktok_downloader_backend/static/`

## Step 7: Reload Web App

1. Go to **Web** tab
2. Click the green **Reload** button
3. Your app should now be running!

## Step 8: Test Your API

Your API will be available at:
```
https://yourusername.pythonanywhere.com/
```

Test endpoints:
- `https://yourusername.pythonanywhere.com/` - Root endpoint
- `https://yourusername.pythonanywhere.com/docs` - API documentation (if enabled)
- `https://yourusername.pythonanywhere.com/download` - Download endpoint

## Troubleshooting

### Error: "No module named 'api_server'"

- Check that your project path in WSGI file is correct
- Ensure virtual environment is activated in WSGI file
- Verify all dependencies are installed in the virtual environment

### Error: "No module named 'asgiref'"

- Run: `pip install asgiref` in your virtual environment
- Regenerate requirements.txt: `poetry export -f requirements.txt --output requirements.txt --without-hashes`

### Error: "Application object must be callable"

- Ensure `wsgi.py` exports `application` (not `app`)
- Check that WSGI file imports from `wsgi` module correctly

### Files Not Being Cleaned Up

- Background tasks in FastAPI work, but PythonAnywhere free tier has limitations
- Files are cleaned up after 1 hour automatically
- Check server logs for cleanup messages

### API Key Not Working

- Verify `.env` file exists in project root
- Check that `python-dotenv` is installed
- Restart web app after changing `.env`

## File Structure

Your project should have this structure:
```
tiktok_downloader_backend/
├── api_server.py          # Main FastAPI application
├── wsgi.py                # WSGI wrapper (for PythonAnywhere)
├── schemas.py             # Pydantic models
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── downloaders/
│   └── tiktok_downloader.py
└── ...
```

## Updating Your App

1. Pull latest changes (if using Git):
   ```bash
   cd ~/tiktok_downloader_backend
   git pull
   ```
2. Update dependencies if needed:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Reload web app in **Web** tab

## Limitations of Free Tier

- **CPU time**: Limited CPU time per day
- **File storage**: Limited disk space
- **Background tasks**: May have limitations
- **HTTPS**: Available but with PythonAnywhere domain
- **Custom domain**: Not available on free tier

## Next Steps

1. Update your Android app's `BASE_URL` to point to your PythonAnywhere URL
2. Test the download functionality
3. Monitor server logs for any issues

## Support

- PythonAnywhere Docs: https://help.pythonanywhere.com/
- FastAPI Docs: https://fastapi.tiangolo.com/
- Check server logs in **Web** tab → **Error log**

