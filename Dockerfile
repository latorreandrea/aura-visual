FROM python:3.11-slim

# Runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Set working directory
WORKDIR /app

# Create a non-root user for better container security
RUN useradd -m appuser

# Copy dependencies first to leverage Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the application files required at runtime
COPY app.py .
COPY aura_visual ./aura_visual

# Adjust ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Start Gunicorn with a bounded timeout
CMD exec gunicorn --bind :$PORT 'aura_visual:create_app("production")' --workers 2 --threads 8 --timeout 60