# API Usage Guide

## Download Endpoint

### POST `/download`

Downloads a TikTok video from the given URL.

**Request:**
```json
{
  "url": "https://www.tiktok.com/@user/video/1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Video downloaded successfully",
  "file_path": "/var/folders/.../tiktok_downloads/#новапошта #доставкамайбутнього #нп_лю #термінал #депо .mp4",
  "file_name": "#новапошта #доставкамайбутнього #нп_лю #термінал #депо .mp4"
}
```

## File Retrieval Endpoint

### GET `/download/file/{file_name}`

Retrieves a downloaded video file.

**Important:** Use the `file_name` field from the download response, and URL encode it if it contains special characters.

### Example Usage

#### Using curl:

```bash
# Step 1: Download the video
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@user/video/1234567890"}'

# Response includes file_name:
# {
#   "file_name": "#новапошта #доставкамайбутнього #нп_лю #термінал #депо .mp4"
# }

# Step 2: Retrieve the file (URL encode the filename)
# For filenames with special characters, use URL encoding:
curl -O "http://localhost:8000/download/file/%23новапошта%20%23доставкамайбутнього%20%23нп_лю%20%23термінал%20%23депо%20.mp4"
```

#### Using Python:

```python
import requests
import urllib.parse

# Download the video
response = requests.post(
    "http://localhost:8000/download",
    json={"url": "https://www.tiktok.com/@user/video/1234567890"}
)
data = response.json()

if data["success"]:
    # Get the file_name from response
    file_name = data["file_name"]
    
    # URL encode the filename
    encoded_filename = urllib.parse.quote(file_name, safe='')
    
    # Retrieve the file
    file_url = f"http://localhost:8000/download/file/{encoded_filename}"
    file_response = requests.get(file_url)
    
    # Save the file
    with open(file_name, 'wb') as f:
        f.write(file_response.content)
    
    print(f"File saved as: {file_name}")
```

#### Using JavaScript/TypeScript:

```javascript
// Download the video
const downloadResponse = await fetch('http://localhost:8000/download', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://www.tiktok.com/@user/video/1234567890' })
});

const data = await downloadResponse.json();

if (data.success) {
  // Get the file_name from response
  const fileName = data.file_name;
  
  // URL encode the filename
  const encodedFileName = encodeURIComponent(fileName);
  
  // Retrieve the file
  const fileUrl = `http://localhost:8000/download/file/${encodedFileName}`;
  const fileResponse = await fetch(fileUrl);
  const blob = await fileResponse.blob();
  
  // Download the file
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  a.click();
}
```

## Notes

1. **Always use `file_name`** from the response, not `file_path`
2. **URL encode the filename** when making the GET request, especially if it contains:
   - Special characters (#, @, %, etc.)
   - Spaces
   - Non-ASCII characters (Cyrillic, Chinese, etc.)
3. The endpoint accepts both:
   - Just the filename (recommended): `#новапошта .mp4` (URL encoded)
   - Full path: `/var/folders/.../file.mp4` (if the file exists at that path)

## Common Issues

- **404 File not found**: Make sure you're using the `file_name` from the response and URL encoding it properly
- **Special characters**: Always URL encode filenames with special characters
- **Spaces**: Spaces should be encoded as `%20` or `+` (then replaced with `%20`)

