FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies for image processing and Lottie
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Create all required directories
RUN mkdir -p /app/uploads/thumbnails \
    /app/uploads/previews \
    /app/uploads/lottie \
    /app/uploads/images/png \
    /app/uploads/images/gif \
    /app/uploads/videos/mp4 \
    /app/uploads/videos/webm \
    /app/exports \
    /app/db

# Set proper permissions
RUN chmod -R 755 /app/uploads /app/exports /app/db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

EXPOSE 8001

# Use uvicorn for production
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]


