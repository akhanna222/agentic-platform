FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy application files
COPY requirements.txt .
COPY . .

# Install Python dependencies
RUN uv pip install --system -r requirements.txt

# Create workspace directory
RUN mkdir -p /app/workspace

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "main.py"]
