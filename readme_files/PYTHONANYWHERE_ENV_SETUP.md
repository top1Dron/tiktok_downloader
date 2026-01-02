# Setting Environment Variables on PythonAnywhere

There are two ways to set environment variables on PythonAnywhere. The **Web tab method (Option 2)** is often more reliable.

## Option 1: Using .env File (Improved)

The Flask app now automatically searches for `.env` files in multiple locations:

1. **Create `.env` file** in your project directory:
   ```bash
   cd ~/tiktok_downloader_backend
   nano .env
   ```

2. **Add your API key**:
   ```env
   API_KEY=btFMHZSH0lx3VldHMc60USPXR901F6nl
   ```

3. **Save and exit** (Ctrl+X, then Y, then Enter)

4. **Reload your web app** in the Web tab

The app will automatically find and load the `.env` file from:
- Same directory as `api_server_flask.py`
- Home directory (`~/.env`)
- Project directory (`~/tiktok_downloader_backend/.env`)
- Current working directory

## Option 2: Using PythonAnywhere Web Tab (Recommended)

This method is more reliable because PythonAnywhere sets these variables before your app starts.

1. **Go to Web tab** in PythonAnywhere Dashboard
2. **Click on your web app** (e.g., `ttdownloader.pythonanywhere.com`)
3. **Scroll down to "Environment variables"** section
4. **Add a new environment variable**:
   - **Variable name**: `API_KEY`
   - **Variable value**: `btFMHZSH0lx3VldHMc60USPXR901F6nl`
5. **Click "Add"**
6. **Click the green "Reload" button** at the top

## Verify Environment Variables Are Loaded

After reloading, you can check if the API key is loaded correctly:

1. **Visit the debug endpoint**:
   ```
   https://yourusername.pythonanywhere.com/debug/config
   ```

2. **You should see**:
   ```json
   {
     "api_key_status": "set (ends with: ...6nl)",
     "api_key_required": true,
     "env_file_checked": true
   }
   ```

If you see `"api_key_status": "not set"`, the environment variable is not being loaded.

## Troubleshooting

### API Key Still Not Working?

1. **Check the error logs**:
   - Go to Web tab
   - Click "Error log" link
   - Look for messages like:
     - `✅ Loaded .env file from: /path/to/.env`
     - `✅ API_KEY loaded: ***6nl`
     - `⚠️ WARNING: API_KEY not set or using default value!`

2. **Verify the API key matches**:
   - Check your Android app's `app.env` file has the same `API_KEY`
   - The key must match exactly (case-sensitive, no extra spaces)

3. **Try Option 2 (Web tab method)**:
   - This is more reliable than `.env` files on PythonAnywhere
   - Environment variables set in Web tab are always available

4. **Check PythonAnywhere's WSGI file**:
   - Make sure it's pointing to the correct project directory
   - The WSGI file should set the working directory (our `wsgi.py` does this)

### Still Getting 401 Unauthorized?

1. **Verify the API key in your Android app**:
   - Check `app/src/main/assets/app.env`
   - Make sure `API_KEY` matches exactly

2. **Test with curl**:
   ```bash
   curl -X POST https://yourusername.pythonanywhere.com/download \
     -H "Content-Type: application/json" \
     -H "X-API-Key: btFMHZSH0lx3VldHMc60USPXR901F6nl" \
     -d '{"url": "https://www.tiktok.com/t/ZThJMSDvK/"}'
   ```

3. **Check request headers**:
   - The Android app should send `X-API-Key` header
   - Verify in Android logs that the header is being sent

