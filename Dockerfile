FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for cryptography
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Expose port for FastMCP SSE server
EXPOSE 3001

# Environment variables
ENV PYTHONPATH=/app
ENV PROXY_HOST=0.0.0.0
ENV PROXY_PORT=3001
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3001/.well-known/oauth-authorization-server || exit 1

# Run FastMCP server with verbose output
CMD ["python", "-u", "src/fastmcp_proxy.py"]
