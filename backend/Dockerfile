FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

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
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Create uploads directory
RUN mkdir -p /app/uploads/thumbnails /app/uploads/previews /app/uploads/lottie /app/uploads/images/png /app/uploads/images/gif /app/uploads/videos/mp4 /app/uploads/videos/webm

EXPOSE 8001

CMD ["python", "server.py"]


