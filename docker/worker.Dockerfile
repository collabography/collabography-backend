FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV (libGL, glib, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libgl1 \
       libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and worker code
COPY app/ ./app/
COPY worker/ ./worker/

# Default command: run Celery worker
CMD ["celery", "-A", "worker.celery_app.celery_app", "worker", "--loglevel=info"]

