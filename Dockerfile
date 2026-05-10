# --- Build stage: install dependencies ---
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/deps -r requirements.txt

# --- Runtime stage ---
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

RUN useradd -m appuser

# Copy only installed packages from builder
COPY --from=builder /deps /usr/local

# Copy only the application files required at runtime
COPY app.py .
COPY aura_visual ./aura_visual

RUN chown -R appuser:appuser /app
USER appuser


CMD exec gunicorn --bind :$PORT 'aura_visual:create_app("production")' --workers 1 --threads 4 --timeout 60