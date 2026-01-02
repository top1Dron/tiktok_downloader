# WebSocket Usage Guide

This guide explains how to connect to the TikTok Downloader API WebSocket endpoint to receive real-time download updates.

## WebSocket Endpoint

**URL Pattern:** `ws://<server_url>/ws/<client_id>`

- **Server URL:** Your API server address (e.g., `localhost:8000` or `192.168.1.100:8000`)
- **Client ID:** A unique identifier for your client (e.g., `android_client_1`, `web_client_1`)

**Example:** `ws://localhost:8000/ws/android_client_1`

## Message Format

### Messages Sent by Server

The server sends JSON messages with the following structure:

```json
{
  "task_id": "uuid-string",
  "status": "pending|downloading|completed|failed",
  "file_name": "video.mp4",
  "file_path": "/path/to/video.mp4",
  "url": "https://tiktok.com/...",
  "error": "Error message (only if status is 'failed')"
}
```

### Messages Sent by Client

You can send any text message to keep the connection alive. The server will respond with a pong:

```json
{
  "type": "pong",
  "client_id": "your_client_id"
}
```

## Connection Examples

### Python Client

Use the provided `websocket_client_example.py`:

```bash
# Basic usage
python websocket_client_example.py

# With custom server and client ID
python websocket_client_example.py ws://localhost:8000 my_client_1
```

Or use it programmatically:

```python
import asyncio
from websocket_client_example import connect_websocket

# Connect and listen for updates
asyncio.run(connect_websocket("ws://localhost:8000", "my_client_1"))
```

### JavaScript/Web Client

Open the provided `websocket_client_javascript.html` file in a web browser, or use the code in your web application:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/web_client_1');

ws.onopen = function(event) {
    console.log('Connected to WebSocket');
    // Send a ping
    ws.send(JSON.stringify({type: 'ping'}));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Download update:', data);
    
    if (data.status === 'completed') {
        console.log('Download completed:', data.file_name);
    } else if (data.status === 'failed') {
        console.error('Download failed:', data.error);
    }
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

ws.onclose = function(event) {
    console.log('WebSocket closed');
};
```

### Android/Kotlin Client

Use the provided `WebSocketService.kt` class:

```kotlin
import com.tiktokdownloader.app.WebSocketService
import kotlinx.coroutines.lifecycleScope
import androidx.lifecycle.lifecycleScope

class MainActivity : AppCompatActivity() {
    private lateinit var webSocketService: WebSocketService
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize WebSocket service
        webSocketService = WebSocketService(
            baseUrl = "ws://10.0.2.2:8000", // Use your server URL
            clientId = "android_client_1",
            apiKey = "your-api-key" // Optional
        )
        
        // Observe download updates
        lifecycleScope.launch {
            webSocketService.downloadUpdates.collect { update ->
                update?.let {
                    when (it.status) {
                        "completed" -> {
                            // Handle completed download
                            Log.d("MainActivity", "Download completed: ${it.fileName}")
                        }
                        "failed" -> {
                            // Handle failed download
                            Log.e("MainActivity", "Download failed: ${it.error}")
                        }
                        else -> {
                            // Handle other statuses
                            Log.d("MainActivity", "Status: ${it.status}")
                        }
                    }
                }
            }
        }
        
        // Observe connection status
        lifecycleScope.launch {
            webSocketService.connectionStatus.collect { status ->
                when (status) {
                    WebSocketService.ConnectionStatus.Connected -> {
                        Log.d("MainActivity", "WebSocket connected")
                    }
                    WebSocketService.ConnectionStatus.Disconnected -> {
                        Log.d("MainActivity", "WebSocket disconnected")
                    }
                    WebSocketService.ConnectionStatus.Error -> {
                        Log.e("MainActivity", "WebSocket error")
                    }
                    else -> {}
                }
            }
        }
        
        // Connect
        webSocketService.connect()
    }
    
    override fun onDestroy() {
        super.onDestroy()
        webSocketService.disconnect()
    }
}
```

## Integration with Download Flow

1. **Start a download** via the REST API:
   ```bash
   POST /download
   {
     "url": "https://www.tiktok.com/..."
   }
   ```
   Response includes a `task_id`.

2. **Connect to WebSocket** before or after starting the download.

3. **Receive updates** automatically when the download status changes:
   - `pending` → Download queued
   - `downloading` → Download in progress
   - `completed` → Download finished (includes `file_name` and `file_path`)
   - `failed` → Download failed (includes `error` message)

4. **Use the file** once status is `completed`:
   - Download the file via: `GET /download/file/{file_name}`
   - Or use the `file_path` if you have server access

## Connection Management

### Keep Connection Alive

- The server expects periodic messages to keep the connection alive
- Send any message (e.g., `{"type": "ping"}`) every 30-60 seconds
- The Python and JavaScript examples handle this automatically

### Reconnection

If the connection drops, implement reconnection logic:

```python
import asyncio
import websockets

async def connect_with_reconnect(url, client_id, max_retries=5):
    for attempt in range(max_retries):
        try:
            await connect_websocket(url, client_id)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Reconnecting in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                raise
```

### Multiple Clients

Each client should use a unique `client_id`. The server maintains separate connections for each client ID.

## Testing

1. **Start the API server:**
   ```bash
   python api_server.py
   ```

2. **Open the HTML test client:**
   - Open `websocket_client_javascript.html` in a browser
   - Enter server URL and client ID
   - Click "Connect"

3. **Start a download** (in another terminal):
   ```bash
   curl -X POST http://localhost:8000/download \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-secret-api-key-change-this" \
     -d '{"url": "https://www.tiktok.com/@user/video/123"}'
   ```

4. **Watch for updates** in the WebSocket client - you should see status updates as the download progresses.

## Troubleshooting

### Connection Refused
- Ensure the API server is running
- Check the server URL is correct
- Verify firewall settings allow WebSocket connections

### No Messages Received
- Check that downloads are actually being started
- Verify the WebSocket connection is established (check connection status)
- Ensure the server is sending updates (check server logs)

### Connection Drops
- Implement ping/pong to keep connection alive
- Add reconnection logic
- Check network stability

## Notes

- WebSocket connections are per-client-ID
- All connected clients receive all download updates (broadcast)
- The server automatically removes disconnected clients
- WebSocket messages are JSON-encoded strings

