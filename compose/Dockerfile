FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install Poetry export plugin (required for poetry export command)
RUN poetry self add poetry-plugin-export || true

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to create venv in project
RUN poetry config virtualenvs.in-project true

# Generate requirements.txt from Poetry (for compatibility with tools that need it)
# This is generated in the container but not committed to git
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --no-interaction || \
    (echo "Warning: poetry export failed, using poetry install only" && touch requirements.txt)

# Install dependencies using Poetry
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run the application
CMD ["poetry", "run", "uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]

