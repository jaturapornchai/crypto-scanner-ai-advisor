@echo off
echo ===== CCXT Fix: Cross-Platform Docker Build =====
echo.

REM Clean up completely first
echo Cleaning up Docker environment...
docker stop crypto-scanner-ai-advisor 2>nul
docker rm crypto-scanner-ai-advisor 2>nul
docker rmi crypto-scanner-ai-advisor:latest 2>nul

REM Remove Python cache files
echo Removing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

REM Build with Linux platform specification
echo Building Docker image for Linux platform...
docker build --platform linux/amd64 --no-cache -t crypto-scanner-ai-advisor:latest .

if %errorlevel% neq 0 (
    echo ❌ Main build failed, trying alternative Dockerfile...
    docker build --platform linux/amd64 --no-cache -f Dockerfile.alternative -t crypto-scanner-ai-advisor:latest .
    
    if %errorlevel% neq 0 (
        echo ❌ Alternative build also failed
        goto :error
    )
)

echo ✅ Docker image built successfully

REM Test critical imports
echo Testing CCXT import...
docker run --rm --platform linux/amd64 crypto-scanner-ai-advisor:latest python -c "import ccxt; print('CCXT version:', ccxt.__version__); print('✅ CCXT import successful')"

if %errorlevel% neq 0 (
    echo ❌ CCXT import test failed
    goto :error
)

echo Testing other imports...
docker run --rm --platform linux/amd64 crypto-scanner-ai-advisor:latest python -c "import numpy; import pandas; import requests; print('✅ All imports successful')"

if %errorlevel% neq 0 (
    echo ❌ Other imports test failed
    goto :error
)

echo ✅ All tests passed!
echo.
echo ===== READY FOR DEPLOYMENT =====
echo.
echo Option 1: Save image for manual transfer
echo   docker save crypto-scanner-ai-advisor:latest ^| gzip ^> crypto-scanner-ai-advisor.tar.gz
echo.
echo Option 2: Push to Docker Hub
echo   docker tag crypto-scanner-ai-advisor:latest jaturapornchai/crypto-scanner-ai-advisor:latest
echo   docker push jaturapornchai/crypto-scanner-ai-advisor:latest
echo.
echo Option 3: Test locally
echo   docker run --rm --name crypto-scanner-ai-advisor-test crypto-scanner-ai-advisor:latest
echo.
goto :end

:error
echo ❌ Build process failed
echo.
echo Try these troubleshooting steps:
echo 1. Ensure Docker Desktop is running with Linux containers
echo 2. Check if WSL2 is properly configured
echo 3. Try building without --platform flag
echo 4. Check the Dockerfile for syntax errors
echo.

:end
pause
