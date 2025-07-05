# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Install system dependencies for nsjail and Python libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libnl-3-dev \
    libnl-route-3-dev \
    libprotobuf-dev \
    protobuf-compiler \
    git \
    bison \
    flex \
    && rm -rf /var/lib/apt/lists/*

# Build and install nsjail
RUN git clone https://github.com/google/nsjail.git /tmp/nsjail \
    && cd /tmp/nsjail \
    && make \
    && cp nsjail /usr/bin/ \
    && rm -rf /tmp/nsjail

# Create non-root user for running the application
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create necessary directories and set permissions
RUN mkdir -p /tmp/sandbox \
    && chmod 755 /tmp/sandbox

# Switch to non-root user
USER appuser

# Expose port 8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python", "app.py"]
