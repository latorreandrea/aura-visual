FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Create and set the working directory
WORKDIR /app

# Copy and install requirements to improve cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Command to start the application with Gunicorn
CMD exec gunicorn --bind :$PORT 'aura_visual:create_app("production")' --workers 2 --threads 8 --timeout 0