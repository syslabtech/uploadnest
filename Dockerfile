# ---- Backend Dockerfile ----
FROM python:3.12-slim as base

# Set workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and config
COPY main.py ./
COPY app/ ./app/

# Create empty .env file (to be mounted or overwritten in production)
RUN touch .env

# Create non-root user
RUN useradd -u 10001 appuser && chown -R appuser /app
USER 10001

# Expose port
EXPOSE 8001

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
