# 🚀 Tread2 Crypto Trading Bot - Deployment Guide

## 🏗️ Build และ Push Image

### 1. Login Docker Hub (ครั้งแรกเท่านั้น)
```bash
docker login
```

### 2. Build และ Push Image
```bash
# Build multi-platform และ push ขึ้น Docker Hub
docker buildx build --platform linux/amd64 --no-cache -t jaturapornchai/tread2:latest --push .
```

---

## 🌐 Server Deployment

### 1. Connect to Server
```bash
ssh root@178.128.55.234
# password : 19682511
```

### 2. Prepare Deployment Directory
```bash
cd /mnt/volume_sgp1_02/jeadbot
```

### 3. Create Environment File (.env)
```bash
# สร้าง .env file
cat > .env << 'EOF'
# Binance API Configuration
BINANCE_API_KEY=xz3oxKAcLPRJxgQvBOSqNGyJipzOoiAvRXwvaHZBYSyHFEfegRwV37Blmwwpxp4z
BINANCE_SECRET_KEY=h9LCIdryqVCEPn6JgGSnmycgtc7FRtKnrSVcqOFVmJ3bOChZDvGBcOCnCdOhvFlT

# DeepSeek AI API Configuration
DEEPSEEK_API_KEY=sk-5056c250d56544a29b3a9240f8e4b2ed
AI_BASE_URL=https://api.deepseek.com

# Trading Configuration
USE_TESTNET=false
TZ=Asia/Bangkok
EOF
```

### 4. Create Docker Compose File
```bash
# สร้าง docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  tread2:
    image: jaturapornchai/tread2:latest
    container_name: tread2-crypto-scanner
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - TZ=Asia/Bangkok
    volumes:
      - ./logs:/root/logs
      - ./.env:/root/.env:ro
    networks:
      - crypto-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  crypto-network:
    driver: bridge
EOF
```

---

## 🚀 Deployment Commands

### 1. Full Deployment (First time)
```bash
# Create directories
mkdir -p logs

# Pull latest image
docker-compose pull

# Start container
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 2. Update Existing Deployment
```bash
# Stop existing container
docker-compose stop

# Pull latest image
docker-compose pull

# Remove old container
docker-compose rm -f

# Start new container
docker-compose up -d

# Check logs
docker-compose logs -f tread2
```

### 3. Quick Restart
```bash
docker-compose restart tread2
```

---

## 📊 Monitoring Commands

### Check Status
```bash
# Container status
docker-compose ps

# Real-time logs
docker-compose logs -f tread2

# Container resources
docker stats tread2-crypto-scanner
```

### Debug Commands
```bash
# Enter container shell
docker exec -it tread2-crypto-scanner sh

# Check environment variables
docker exec tread2-crypto-scanner env | grep -E "(BINANCE|DEEPSEEK)"

# Check .env file in container
docker exec tread2-crypto-scanner cat /root/.env
```

---

## 🛠️ Troubleshooting

### 1. .env file not found
```bash
# Check if .env exists on host
ls -la .env

# Check if .env mounted in container
docker exec tread2-crypto-scanner ls -la /root/.env

# Recreate .env file
nano .env
```

### 2. API Connection Issues
```bash
# Test API connection
docker exec tread2-crypto-scanner sh -c "ping -c 3 api.binance.com"
docker exec tread2-crypto-scanner sh -c "ping -c 3 api.deepseek.com"
```

### 3. Full Clean Restart
```bash
# Stop and remove everything
docker-compose down -v

# Clean Docker system
docker system prune -f

# Restart
docker-compose up -d
```

---

## ⚡ Quick Reference

```bash
# Start
docker-compose up -d

# Stop
docker-compose stop

# Restart
docker-compose restart

# Update
docker-compose pull && docker-compose up -d

# Logs
docker-compose logs -f

# Debug
docker exec -it tread2-crypto-scanner sh
