# Backend Dockerfile for Cloud Run
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Set environment variables for Cloud Run
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port (Cloud Run uses 8080 by default)
EXPOSE 8080

# Run the application with uvicorn
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}