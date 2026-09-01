# Dockerfile — reproducible build environment for AeonMosaic
# Usage:
#   docker build -t aeonmosaic:dev .
#   docker run --rm -it aeonmosaic:dev pytest tests/ -v

FROM python:3.11-slim AS base

LABEL org.opencontainers.image.title="AeonMosaic"
LABEL org.opencontainers.image.description="Pleromic modular robot — Unified Master Blueprint v0.2"
LABEL org.opencontainers.image.authors="Micheal Landry (@MyKey00110000)"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/TaoishTechy/AeonMosaic"

# System deps for numpy/scipy/sympy wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching)
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[test,dev]"

# Copy the rest of the source
COPY . .

# Run as a non-root user
RUN useradd -m -u 1000 aeon && chown -R aeon:aeon /app
USER aeon

# Default: run the test suite
CMD ["pytest", "tests/", "-v"]
