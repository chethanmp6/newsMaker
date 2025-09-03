FROM python:3.11-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the project
ADD . /app
WORKDIR /app

# Install dependencies with uv
RUN uv sync --frozen --no-cache

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libasound2-dev \
    portaudio19-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder stage
COPY --from=builder --chown=app:app /app /app

# Set PATH to include virtual environment
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/src

# Create directories
RUN mkdir -p /app/data/knowledge_bases /app/data/media_cache /app/data/audio_cache /app/data/output_videos /app/logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8001

# Set PYTHONPATH
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Start command  
CMD ["python", "-m", "kannada_news_automation.main"]