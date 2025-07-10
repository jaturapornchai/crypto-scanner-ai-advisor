#!/bin/bash
# Cross-platform Docker build script for Windows to Linux deployment

echo "=== Docker Cross-Platform Build Script ==="
echo "Building Docker image for Linux deployment from Windows..."

# Clean up any existing containers and images
echo "Cleaning up existing containers and images..."
docker stop crypto-scanner-ai-advisor 2>/dev/null || true
docker rm crypto-scanner-ai-advisor 2>/dev/null || true
docker rmi crypto-scanner-ai-advisor:latest 2>/dev/null || true

# Remove any Python cache files that might cause issues
echo "Cleaning Python cache files..."
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Build the Docker image with explicit Linux platform
echo "Building Docker image for Linux platform..."
docker build --platform linux/amd64 --no-cache -t crypto-scanner-ai-advisor:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully for linux/amd64"
    
    # Test the image locally
    echo "Testing the Docker image..."
    docker run --rm --platform linux/amd64 crypto-scanner-ai-advisor:latest python -c "import ccxt; import numpy; import pandas; print('All imports successful')"
    
    if [ $? -eq 0 ]; then
        echo "✅ Docker image test passed"
        echo ""
        echo "=== Next Steps ==="
        echo "1. Save the image: docker save crypto-scanner-ai-advisor:latest | gzip > crypto-scanner-ai-advisor.tar.gz"
        echo "2. Transfer to Linux server: scp crypto-scanner-ai-advisor.tar.gz user@server:/path/"
        echo "3. Load on Linux server: gunzip -c crypto-scanner-ai-advisor.tar.gz | docker load"
        echo "4. Run on Linux server: docker run -d --name crypto-scanner-ai-advisor crypto-scanner-ai-advisor:latest"
    else
        echo "❌ Docker image test failed"
    fi
else
    echo "❌ Docker build failed"
fi
