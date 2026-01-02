#!/bin/bash

# Setup script for TikTok Downloader project

echo "Setting up TikTok Downloader project..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Poetry is not installed. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Configure Poetry to use venv folder in project directory
echo "Configuring Poetry to use local venv folder..."
poetry config virtualenvs.in-project true

# Install Python dependencies
echo "Installing Python dependencies..."
poetry install

echo ""
echo "Setup complete!"
echo ""
echo "To run the API server:"
echo "  poetry run python api_server.py"
echo ""
echo "To build the Android APK:"
echo "  See android_app/BUILD_INSTRUCTIONS.md"
echo ""

