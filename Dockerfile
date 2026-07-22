# ─────────────────────────────────────────────────────────────────
# HydroThermal Nexus-AI v2.0 — Production Dockerfile
# Streamlit (port 8501) + FastAPI backend (port 8001)
# ─────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Metadata labels
LABEL org.opencontainers.image.title="HydroThermal Nexus-AI"
LABEL org.opencontainers.image.version="2.0.0"
LABEL org.opencontainers.image.description="Industrial IoT Operational Cockpit"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root app user for security
RUN useradd -m -u 1000 -s /bin/bash nexususer

WORKDIR /app

# Install Python dependencies (cache layer)
COPY requirements-streamlit.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-streamlit.txt

# Copy application source
COPY . .

# Create persistent data directory and set ownership
RUN mkdir -p /app/data /app/assets \
    && chown -R nexususer:nexususer /app

# Switch to non-root user
USER nexususer

# Expose both ports
EXPOSE 8501 8001

# Health check for Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    NEXUS_API_SECRET=NexusAPI_Internal_2026

# Run Streamlit (FastAPI starts as background thread inside app.py)
ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0", \
            "--server.headless=true", \
            "--browser.gatherUsageStats=false"]