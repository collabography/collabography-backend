FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and worker code
COPY app/ ./app/
COPY worker/ ./worker/

# Run Celery worker
CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info"]

