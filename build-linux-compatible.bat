@echo off
REM Cross-platform Docker build script for Windows to Linux deployment

echo === Docker Cross-Platform Build Script ===
echo Building Docker image for Linux deployment from Windows...

REM Clean up any existing containers and images
echo Cleaning up existing containers and images...
docker stop crypto-scanner-ai-advisor 2>nul
docker rm crypto-scanner-ai-advisor 2>nul
docker rmi crypto-scanner-ai-advisor:latest 2>nul

REM Remove any Python cache files that might cause issues
echo Cleaning Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

REM Build the Docker image with explicit Linux platform
echo Building Docker image for Linux platform...
docker build --platform linux/amd64 --no-cache -t crypto-scanner-ai-advisor:latest .

if %errorlevel% equ 0 (
    echo ✅ Docker image built successfully for linux/amd64
    
    REM Test the image locally
    echo Testing the Docker image...
    docker run --rm --platform linux/amd64 crypto-scanner-ai-advisor:latest python -c "import ccxt; import numpy; import pandas; print('All imports successful')"
    
    if %errorlevel% equ 0 (
        echo ✅ Docker image test passed
        echo.
        echo === Next Steps ===
        echo 1. Save the image: docker save crypto-scanner-ai-advisor:latest ^| gzip ^> crypto-scanner-ai-advisor.tar.gz
        echo 2. Transfer to Linux server: scp crypto-scanner-ai-advisor.tar.gz user@server:/path/
        echo 3. Load on Linux server: gunzip -c crypto-scanner-ai-advisor.tar.gz ^| docker load
        echo 4. Run on Linux server: docker run -d --name crypto-scanner-ai-advisor crypto-scanner-ai-advisor:latest
    ) else (
        echo ❌ Docker image test failed
    )
) else (
    echo ❌ Docker build failed
)

pause
