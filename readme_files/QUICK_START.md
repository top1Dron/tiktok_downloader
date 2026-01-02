# Quick Start Guide

## Prerequisites

- Python 3.14+
- Poetry (will be installed by setup script if not present)
- Android Studio (for building APK)

## Setup

1. **Install Python dependencies:**
   ```bash
   ./bash_scripts/setup.sh
   ```
   Or manually:
   ```bash
   poetry config virtualenvs.in-project true
   poetry install
   ```
   
   Note: The setup script configures Poetry to create a `.venv` folder in the project directory. This keeps the virtual environment local to the project.

2. **Start the API server:**
   ```bash
   poetry run python api_server.py
   ```
   The server will run on `http://localhost:8000`

## Building the Android APK

### Option 1: Using Android Studio (Easiest)

1. Open Android Studio
2. Open the `android_app` folder
3. Wait for Gradle sync
4. Build > Build Bundle(s) / APK(s) > Build APK(s)
5. APK location: `android_app/app/build/outputs/apk/debug/app-debug.apk`

### Option 2: Command Line

```bash
cd android_app
chmod +x gradlew  # If on Mac/Linux
./gradlew assembleDebug
```

## Configuring the Android App

**Important:** Before using the app, update the API server URL:

1. Open `android_app/app/src/main/java/com/tiktokdownloader/app/ApiService.kt`
2. Update `BASE_URL`:
   - **Emulator**: `http://10.0.2.2:8000/` (default)
   - **Physical Device**: `http://YOUR_COMPUTER_IP:8000/`
     - Find your IP: `ifconfig` (Mac/Linux) or `ipconfig` (Windows)
3. Rebuild the APK

## Usage

### Python Class (Direct Usage)

```python
from downloaders.tiktok_downloader import TikTokDownloader

downloader = TikTokDownloader()
file_path = downloader.download("https://www.tiktok.com/@user/video/1234567890")
print(f"Downloaded to: {file_path}")
```

### Android App

1. Start the Python API server
2. Install the APK on your device/emulator
3. Open the app
4. Enter a TikTok URL
5. Tap "Download Video"
6. The video will be saved to your device's Downloads folder

## Testing the API

```bash
# Test download endpoint
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@user/video/1234567890"}'
```

## Troubleshooting

- **"Connection refused"**: Make sure the Python server is running
- **"Invalid TikTok URL"**: Ensure the URL contains "tiktok.com"
- **Build errors**: Make sure Android SDK and build tools are up to date
- **Permission errors**: Grant storage permissions when prompted

