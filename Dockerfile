# Multi-stage build to ensure Linux compatibility
FROM python:3.11-slim AS builder

# Set environment variables for optimization
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_NUM_THREADS=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .

# Clean install Python dependencies in builder stage
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip cache purge && \
    rm -rf /root/.cache/pip && \
    pip install --no-cache-dir --no-compile --force-reinstall ccxt==4.2.25 && \
    pip install --no-cache-dir --no-compile --force-reinstall -r requirements.txt

# Final stage - clean runtime image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_NUM_THREADS=1
ENV PYTHONPATH=/app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Create logs directory  
RUN mkdir -p logs

# Remove any __pycache__ and .pyc files that might cause issues
RUN find . -type f -name "*.pyc" -delete && \
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Test imports before running
RUN python -c "import ccxt; print('CCXT import successful')" && \
    python -c "import numpy; print('NumPy import successful')" && \
    python -c "import pandas; print('Pandas import successful')"

# Run the application with unbuffered output
CMD ["python", "-u", "app.py"]
