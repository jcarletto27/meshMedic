FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN mkdir -p /tmp/stl_processing && \
    chown -R appuser:appgroup /tmp/stl_processing && \
    chmod 700 /tmp/stl_processing

USER appuser
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
