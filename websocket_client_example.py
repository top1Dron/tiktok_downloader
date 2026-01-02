"""
Example WebSocket client for connecting to the TikTok Downloader API.
This demonstrates how to connect and receive real-time download updates.
"""

import asyncio
import websockets
import json
import sys


async def connect_websocket(server_url: str = "ws://localhost:8000", client_id: str = "client_1"):
    """
    Connect to the WebSocket endpoint and listen for messages.
    
    Args:
        server_url: Base URL of the server (without /ws/)
        client_id: Unique client identifier
    """
    websocket_url = f"{server_url}/ws/{client_id}"
    
    print(f"Connecting to {websocket_url}...")
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            print(f"Connected! Client ID: {client_id}")
            print("Listening for download updates...")
            print("(Send any message to keep connection alive, or Ctrl+C to exit)\n")
            
            # Send a ping message to test the connection
            await websocket.send(json.dumps({"type": "ping"}))
            
            # Listen for messages
            while True:
                try:
                    # Wait for a message (with timeout to allow keyboard interrupt)
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    
                    # Parse and display the message
                    try:
                        data = json.loads(message)
                        print(f"Received update:")
                        print(f"  Task ID: {data.get('task_id', 'N/A')}")
                        print(f"  Status: {data.get('status', 'N/A')}")
                        print(f"  File Name: {data.get('file_name', 'N/A')}")
                        print(f"  File Path: {data.get('file_path', 'N/A')}")
                        print(f"  URL: {data.get('url', 'N/A')}")
                        if data.get('error'):
                            print(f"  Error: {data.get('error')}")
                        print()
                    except json.JSONDecodeError:
                        print(f"Received (raw): {message}")
                        
                except asyncio.TimeoutError:
                    # Timeout is expected, just continue the loop
                    continue
                    
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed by server")
    except KeyboardInterrupt:
        print("\nDisconnecting...")
    except Exception as e:
        print(f"Error: {e}")


async def connect_and_send_ping(server_url: str = "ws://localhost:8000", client_id: str = "client_1"):
    """
    Connect and periodically send ping messages to keep connection alive.
    """
    websocket_url = f"{server_url}/ws/{client_id}"
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            print(f"Connected to {websocket_url}")
            
            # Send periodic pings
            async def send_pings():
                while True:
                    await asyncio.sleep(30)  # Send ping every 30 seconds
                    await websocket.send(json.dumps({"type": "ping"}))
            
            # Start ping task
            ping_task = asyncio.create_task(send_pings())
            
            # Listen for messages
            try:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    print(f"Update: {json.dumps(data, indent=2)}")
            finally:
                ping_task.cancel()
                
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Get server URL and client ID from command line arguments
    server_url = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8000"
    client_id = sys.argv[2] if len(sys.argv) > 2 else "client_1"
    
    # Remove 'ws://' or 'http://' prefix if present, we'll add it
    if server_url.startswith("http://"):
        server_url = server_url.replace("http://", "ws://")
    elif server_url.startswith("https://"):
        server_url = server_url.replace("https://", "wss://")
    elif not server_url.startswith("ws://") and not server_url.startswith("wss://"):
        server_url = f"ws://{server_url}"
    
    print(f"WebSocket Client Example")
    print(f"Server: {server_url}")
    print(f"Client ID: {client_id}")
    print("-" * 50)
    
    # Run the client
    asyncio.run(connect_websocket(server_url, client_id))

