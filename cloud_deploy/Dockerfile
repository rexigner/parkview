# ─────────────────────────────────────────────
#  Dockerfile  —  Cloud deployment container
# ─────────────────────────────────────────────

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements_normal_deploy.txt .
RUN pip install --no-cache-dir -r requirements_normal_deploy.txt

# Copy application code
COPY . .

# Create database directory if it doesn't exist
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV DB_PATH=/app/data/parking.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; sqlite3.connect('/app/data/parking.db')" || exit 1

# Command to run the bot
CMD ["python", "main.py"]