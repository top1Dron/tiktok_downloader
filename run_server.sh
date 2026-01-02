#!/bin/bash

# Run the TikTok Downloader API server with uvicorn

# Check if we're in the backend directory
if [ ! -f "api_server.py" ]; then
    echo "Error: api_server.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if Poetry is available
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Please install it first."
    exit 1
fi

# Default to reload mode in development
RELOAD=${1:---reload}

if [ "$RELOAD" = "--reload" ] || [ "$RELOAD" = "-r" ]; then
    echo "Starting server with auto-reload (development mode)..."
    poetry run uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Starting server in production mode..."
    poetry run uvicorn api_server:app --host 0.0.0.0 --port 8000
fi

