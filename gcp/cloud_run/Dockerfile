# Multi-stage build for IELTS GenAI Prep on Cloud Run
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies for audio processing
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Set Python environment
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}

# Expose port (Cloud Run injects PORT env var)
EXPOSE 5000

# Use Gunicorn with eventlet workers for WebSocket support
CMD exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 8 \
    --timeout 0 \
    --worker-class eventlet \
    --worker-connections 1000 \
    --keep-alive 65 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    app:app
