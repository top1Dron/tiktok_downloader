#!/bin/bash

# Generate requirements.txt from Poetry for Heroku deployment

echo "Generating requirements.txt from pyproject.toml..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Please install it first:"
    echo "  pip install poetry"
    exit 1
fi

# Generate requirements.txt
poetry export -f requirements.txt --output requirements.txt --without-hashes --no-interaction

if [ $? -eq 0 ]; then
    echo "✓ requirements.txt generated successfully"
    echo "  File location: $(pwd)/requirements.txt"
else
    echo "✗ Failed to generate requirements.txt"
    echo "  You may need to install the poetry export plugin:"
    echo "  poetry self add poetry-plugin-export"
    exit 1
fi

