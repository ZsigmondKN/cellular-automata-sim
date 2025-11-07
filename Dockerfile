FROM python:3.8-slim


WORKDIR /app

COPY . /app


# Install system dependencies including Tk

RUN apt-get update && apt-get install -y \
    gcc \
    tk-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    numpy==1.24.4 \
    Flask \
    eventlet==0.26.1 \
    Flask-SocketIO==5.3.1 \
    gunicorn==20.0.4 \
    matplotlib 

VOLUME ["/app"]

CMD ["python3", "CAPyle_releaseV2/release/main.py"]
