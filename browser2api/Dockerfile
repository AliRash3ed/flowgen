# FlowGen Studio - Production Dockerfile for Cloud VPS & Google Cloud Run
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    FLOWGEN_HOST=0.0.0.0 \
    FLOWGEN_PORT=8787

WORKDIR /app

# Install system dependencies for headless Chromium & Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    libgbm-dev \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libxshmfence1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package requirements & install
COPY pyproject.toml /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir playwright fastapi uvicorn websockets pillow pydantic && \
    playwright install chromium

# Copy application source
COPY . /app/

# Expose FlowGen HUD & API port
EXPOSE 8787

# Run FlowGen Studio
CMD ["python", "run_hud.py", "--host", "0.0.0.0", "--port", "8787", "--no-browser"]
