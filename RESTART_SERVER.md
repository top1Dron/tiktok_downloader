# Restart the API Server

If you're still seeing the old response format (without `file_name`), you need to **restart the API server**.

## Steps:

1. **Stop the current server** (if running):
   - Press `Ctrl+C` in the terminal where the server is running

2. **Start the server again**:
   ```bash
   poetry run python api_server.py
   ```

3. **Test the new endpoint**:
   ```bash
   curl -X POST http://localhost:8000/download \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.tiktok.com/@user/video/1234567890"}'
   ```

You should now see a response like:
```json
{
  "success": true,
  "message": "Video downloaded successfully",
  "file_path": "/var/folders/.../tiktok_downloads/#новапошта #доставкамайбутнього #нп_лю #термінал #депо .mp4",
  "file_name": "#новапошта #доставкамайбутнього #нп_лю #термінал #депо .mp4"
}
```

**Use the `file_name` field** (not `file_path`) for the `/download/file/{file_name}` endpoint.

