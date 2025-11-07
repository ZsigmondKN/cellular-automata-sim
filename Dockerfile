FROM python:3.8-slim

WORKDIR /app

# Install system dependencies including Tk
RUN apt-get update && apt-get install -y \
    gcc \
    tk-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Default command (can be overridden by docker-compose)
CMD ["python3", "CAPyle_releaseV2/release/main.py"]
