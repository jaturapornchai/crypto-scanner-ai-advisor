# Crypto Scanner AI Advisor - Deployment Guide

## Windows to Linux Cross-Platform Build (RECOMMENDED)

### Prerequisites
- Docker Desktop with Linux containers enabled
- Windows 10/11 with WSL2 (recommended)
- Git Bash or PowerShell

### Step 1: Build Linux-Compatible Docker Image on Windows
```bash
# Method 1: Using the automated script
.\build-linux-compatible.bat

# Method 2: Manual build with explicit Linux platform
docker build --platform linux/amd64 --no-cache -t crypto-scanner-ai-advisor:latest .

# Method 3: Alternative Dockerfile (if main build fails)
docker build --platform linux/amd64 --no-cache -f Dockerfile.alternative -t crypto-scanner-ai-advisor:latest .
```

### Step 2: Test the Image on Windows
```bash
# Test imports to ensure everything works
docker run --rm --platform linux/amd64 crypto-scanner-ai-advisor:latest python -c "
import ccxt; print('CCXT version:', ccxt.__version__)
import numpy; print('NumPy version:', numpy.__version__)
import pandas; print('Pandas version:', pandas.__version__)
print('All imports successful!')
"
```

### Step 3: Export and Transfer to Linux Server
```bash
# Save the image
docker save crypto-scanner-ai-advisor:latest | gzip > crypto-scanner-ai-advisor.tar.gz

# Transfer to Linux server (replace with your server details)
scp crypto-scanner-ai-advisor.tar.gz root@178.128.55.234:/tmp/

# Alternative: Push to Docker Hub
docker tag crypto-scanner-ai-advisor:latest jaturapornchai/crypto-scanner-ai-advisor:latest
docker push jaturapornchai/crypto-scanner-ai-advisor:latest
```

### Step 4: Deploy on Linux Server
```bash
ssh root@178.128.55.234
# password : 19682511

cd /mnt/volume_sgp1_02/jeadbot

# Stop existing container
sudo docker-compose stop

# Method A: Load from transferred file
sudo docker load < /tmp/crypto-scanner-ai-advisor.tar.gz

# Method B: Pull from Docker Hub
sudo docker pull jaturapornchai/crypto-scanner-ai-advisor:latest

# Complete cleanup to avoid cached issues
sudo docker-compose down
sudo docker system prune -af
sudo docker volume prune -f

# Test the image before deployment
sudo docker run --rm -it crypto-scanner-ai-advisor:latest python -c "
import ccxt; print('CCXT version:', ccxt.__version__)
import sys; print('Python:', sys.version)
print('Linux deployment test successful!')
"

# Start with the new image
sudo docker-compose up -d

# Monitor logs
sudo docker logs -f crypto-scanner-ai-advisor
```

## Legacy Build Command (Updated Multi-Stage Build)
```bash
# Clean build with Multi-Stage Dockerfile + LRC 5-lookback + DeepSeek AI + Dynamic AI Confidence Analysis
# Uses optimized multi-stage build for better Linux compatibility and smaller image size
docker buildx build --platform linux/amd64 --no-cache -t jaturapornchai/getspot:latest --push .
```

## Latest System Features (Hourly Position/Order Checking)

The system now includes these enhancements:
- **Hourly Position Monitoring**: Positions and orders checked every hour
- **Minimized Output**: Reduced console noise, essential information only
- **Automatic Maintenance**: Problematic positions/orders fixed automatically
- **Continuous Monitoring**: Better reliability with hourly health checks

### Deploy Commands (Updated for Hourly Monitoring + LRC 5-Lookback + DeepSeek + AI Dynamic Confidence)
```bash
ssh root@178.128.55.234
# password : 19682511

cd /mnt/volume_sgp1_02/jeadbot

# Stop existing container
sudo docker-compose stop

# Pull latest image with AI Dynamic Confidence Analysis
sudo docker pull jaturapornchai/getspot:latest

# Complete cleanup to avoid cached issues (IMPORTANT for CCXT fix)
sudo docker-compose down
sudo docker system prune -af
sudo docker volume prune -f

# Clear Docker cache and corrupted packages
sudo docker builder prune -af

# Test the AI confidence system before deployment
sudo docker run --rm -it jaturapornchai/getspot:latest python -c "import ccxt; print('CCXT OK')"

# If CCXT test fails, rebuild with no-cache
# sudo docker pull jaturapornchai/getspot:latest --platform linux/amd64

# Start with DeepSeek AI + Dynamic Confidence Analysis
sudo docker-compose up -d

# Monitor logs for AI confidence calculations
sudo docker logs -f getspot
```

### CCXT Error Fix (ValueError: bad marshal data)
```bash
# If you get CCXT import error, follow these steps:

# 1. Complete Docker cleanup
sudo docker-compose down
sudo docker system prune -af --volumes
sudo docker builder prune -af

# 2. Remove all Python cache and corrupted packages
sudo docker run --rm -v /var/lib/docker:/var/lib/docker alpine sh -c "find /var/lib/docker -name '*.pyc' -delete"

# 3. Force rebuild without cache
cd /mnt/volume_sgp1_02/jeadbot
sudo docker pull jaturapornchai/getspot:latest --platform linux/amd64

# 4. Test CCXT specifically
sudo docker run --rm -it jaturapornchai/getspot:latest python -c "
import sys; print('Python:', sys.version)
import ccxt; print('CCXT version:', ccxt.__version__)
exchange = ccxt.binance({'sandbox': False, 'enableRateLimit': True})
print('CCXT test successful')
"

# 5. If still fails, restart Docker daemon
sudo systemctl restart docker
sudo docker pull jaturapornchai/getspot:latest

# 6. Start fresh
sudo docker-compose up -d
```

### Emergency CCXT Fix - Rebuild on Server (When Pull Fails)
```bash
# If docker pull still fails with CCXT error, rebuild locally on server:

# 1. Clone/update source code on server
cd /mnt/volume_sgp1_02
git clone https://github.com/your-repo/crypto-scanner-ai-advisor.git jeadbot-new || \
cd jeadbot-new && git pull

# 2. Copy important files from old setup
cp /mnt/volume_sgp1_02/jeadbot/.env /mnt/volume_sgp1_02/jeadbot-new/ || echo "No .env file"
cp /mnt/volume_sgp1_02/jeadbot/docker-compose.yml /mnt/volume_sgp1_02/jeadbot-new/ || echo "No docker-compose.yml"

# 3. Build directly on Linux server (this will compile CCXT properly for Linux)
cd /mnt/volume_sgp1_02/jeadbot-new
sudo docker build --no-cache -t jaturapornchai/getspot:latest-linux .

# 4. Test the locally built image
sudo docker run --rm -it jaturapornchai/getspot:latest-linux python -c "
import sys; print('Python:', sys.version)
import ccxt; print('CCXT version:', ccxt.__version__)
exchange = ccxt.binance({'sandbox': False, 'enableRateLimit': True})
print('CCXT test successful - Linux build!')
"

# 5. If test passes, replace old setup
cd /mnt/volume_sgp1_02
mv jeadbot jeadbot-backup
mv jeadbot-new jeadbot
cd jeadbot

# 6. Update docker-compose.yml to use local image
sed -i 's/jaturapornchai\/getspot:latest/jaturapornchai\/getspot:latest-linux/g' docker-compose.yml

# 7. Start with local Linux-built image
sudo docker-compose up -d

# 8. Monitor
sudo docker logs -f getspot
```

### Alternative: Quick Fix with Different CCXT Version
```bash
# If rebuild takes too long, try with different CCXT version

# 1. Create temporary Dockerfile with older CCXT
cat > Dockerfile.ccxt-fix << 'EOF'
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++ build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install ccxt==4.1.0 python-dotenv requests numpy pandas colorama
COPY . .
RUN mkdir -p logs
CMD ["python", "-u", "app.py"]
EOF

# 2. Build with older CCXT
sudo docker build --no-cache -f Dockerfile.ccxt-fix -t jaturapornchai/getspot:ccxt-fix .

# 3. Test
sudo docker run --rm -it jaturapornchai/getspot:ccxt-fix python -c "import ccxt; print('CCXT OK')"

# 4. Use if test passes
sed -i 's/jaturapornchai\/getspot:latest/jaturapornchai\/getspot:ccxt-fix/g' docker-compose.yml
sudo docker-compose up -d
```
