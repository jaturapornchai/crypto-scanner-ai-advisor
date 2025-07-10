#!/usr/bin/env python3
"""
Cross-Platform Docker Build Test Script
Tests Docker image build process and Linux compatibility from Windows
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path

def run_command(cmd, capture_output=True, shell=True):
    """Run a shell command and return result"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=capture_output, text=True, timeout=300)
        if result.returncode != 0:
            print(f"Command failed with return code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
        return result
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {cmd}")
        return None
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def test_docker_available():
    """Test if Docker is available and running"""
    print("=== Testing Docker availability ===")
    result = run_command("docker --version")
    if result and result.returncode == 0:
        print(f"✅ Docker available: {result.stdout.strip()}")
        return True
    else:
        print("❌ Docker not available")
        return False

def test_platform_support():
    """Test if Docker supports Linux platform builds"""
    print("\n=== Testing Linux platform support ===")
    result = run_command("docker buildx ls")
    if result and result.returncode == 0:
        print("✅ Docker buildx available")
        if "linux/amd64" in result.stdout:
            print("✅ Linux/amd64 platform supported")
            return True
        else:
            print("⚠️  Linux/amd64 platform may not be supported")
            return False
    else:
        print("❌ Docker buildx not available")
        return False

def cleanup_docker():
    """Clean up Docker containers and images"""
    print("\n=== Cleaning up Docker ===")
    
    # Stop and remove containers
    containers = ["crypto-scanner-ai-advisor", "getspot"]
    for container in containers:
        run_command(f"docker stop {container}")
        run_command(f"docker rm {container}")
    
    # Remove images
    images = ["crypto-scanner-ai-advisor:latest", "crypto-scanner-ai-advisor:test"]
    for image in images:
        run_command(f"docker rmi {image}")
    
    # Clean cache
    run_command("docker system prune -f")
    print("✅ Docker cleanup completed")

def test_docker_build():
    """Test Docker build process"""
    print("\n=== Testing Docker build ===")
    
    # Test main Dockerfile
    print("Building with main Dockerfile...")
    result = run_command("docker build --platform linux/amd64 --no-cache -t crypto-scanner-ai-advisor:test .")
    
    if result and result.returncode == 0:
        print("✅ Docker build successful")
        return True
    else:
        print("❌ Docker build failed")
        
        # Try alternative Dockerfile
        print("Trying alternative Dockerfile...")
        result = run_command("docker build --platform linux/amd64 --no-cache -f Dockerfile.alternative -t crypto-scanner-ai-advisor:test .")
        
        if result and result.returncode == 0:
            print("✅ Alternative Docker build successful")
            return True
        else:
            print("❌ Alternative Docker build also failed")
            return False

def test_image_imports():
    """Test critical imports in the Docker image"""
    print("\n=== Testing image imports ===")
    
    test_commands = [
        "import ccxt; print('CCXT version:', ccxt.__version__)",
        "import numpy; print('NumPy version:', numpy.__version__)",
        "import pandas; print('Pandas version:', pandas.__version__)",
        "import requests; print('Requests import successful')",
        "import dotenv; print('Python-dotenv import successful')"
    ]
    
    for cmd in test_commands:
        result = run_command(f'docker run --rm --platform linux/amd64 crypto-scanner-ai-advisor:test python -c "{cmd}"')
        if result and result.returncode == 0:
            print(f"✅ {cmd.split(';')[0]} - OK")
        else:
            print(f"❌ {cmd.split(';')[0]} - FAILED")
            return False
    
    return True

def test_application_start():
    """Test if the application starts correctly"""
    print("\n=== Testing application startup ===")
    
    # Start container in background
    result = run_command("docker run -d --name crypto-scanner-ai-advisor-test --platform linux/amd64 crypto-scanner-ai-advisor:test")
    
    if result and result.returncode == 0:
        print("✅ Container started")
        
        # Wait a bit for startup
        time.sleep(5)
        
        # Check logs
        logs_result = run_command("docker logs crypto-scanner-ai-advisor-test")
        if logs_result and logs_result.returncode == 0:
            print("✅ Application logs available")
            if "error" not in logs_result.stdout.lower():
                print("✅ No obvious errors in startup")
                
                # Stop test container
                run_command("docker stop crypto-scanner-ai-advisor-test")
                run_command("docker rm crypto-scanner-ai-advisor-test")
                return True
            else:
                print("⚠️  Possible errors in startup logs")
        
        # Stop test container
        run_command("docker stop crypto-scanner-ai-advisor-test")
        run_command("docker rm crypto-scanner-ai-advisor-test")
        return False
    else:
        print("❌ Container failed to start")
        return False

def generate_deployment_package():
    """Generate deployment package for Linux server"""
    print("\n=== Generating deployment package ===")
    
    # Tag the image properly
    run_command("docker tag crypto-scanner-ai-advisor:test crypto-scanner-ai-advisor:latest")
    
    # Save image to file
    print("Saving Docker image to file...")
    result = run_command("docker save crypto-scanner-ai-advisor:latest | gzip > crypto-scanner-ai-advisor.tar.gz")
    
    if result and result.returncode == 0:
        # Check file size
        if os.path.exists("crypto-scanner-ai-advisor.tar.gz"):
            size = os.path.getsize("crypto-scanner-ai-advisor.tar.gz")
            print(f"✅ Image saved: crypto-scanner-ai-advisor.tar.gz ({size/1024/1024:.1f} MB)")
            
            # Create deployment script
            deployment_script = """#!/bin/bash
# Auto-generated deployment script for Linux server

echo "=== Crypto Scanner AI Advisor Deployment ==="
echo "Loading Docker image..."

# Load the image
docker load < crypto-scanner-ai-advisor.tar.gz

# Test the image
echo "Testing loaded image..."
docker run --rm crypto-scanner-ai-advisor:latest python -c "
import ccxt; print('CCXT version:', ccxt.__version__)
import sys; print('Python:', sys.version)
print('Linux deployment test successful!')
"

if [ $? -eq 0 ]; then
    echo "✅ Image test successful"
    echo "Ready to deploy with: docker-compose up -d"
else
    echo "❌ Image test failed"
fi
"""
            
            with open("deploy-linux.sh", "w") as f:
                f.write(deployment_script)
            
            print("✅ Deployment script created: deploy-linux.sh")
            return True
        else:
            print("❌ Failed to create image file")
            return False
    else:
        print("❌ Failed to save image")
        return False

def main():
    """Main test function"""
    print("Cross-Platform Docker Build Test Script")
    print("=" * 50)
    
    test_results = []
    
    # Test Docker availability
    if test_docker_available():
        test_results.append(("Docker Available", True))
    else:
        test_results.append(("Docker Available", False))
        print("❌ Docker not available, cannot continue")
        return
    
    # Test platform support
    if test_platform_support():
        test_results.append(("Platform Support", True))
    else:
        test_results.append(("Platform Support", False))
        print("⚠️  Platform support limited, but continuing...")
    
    # Cleanup
    cleanup_docker()
    
    # Test Docker build
    if test_docker_build():
        test_results.append(("Docker Build", True))
    else:
        test_results.append(("Docker Build", False))
        print("❌ Docker build failed, cannot continue")
        return
    
    # Test imports
    if test_image_imports():
        test_results.append(("Image Imports", True))
    else:
        test_results.append(("Image Imports", False))
        print("❌ Image imports failed")
        return
    
    # Test application startup
    if test_application_start():
        test_results.append(("Application Start", True))
    else:
        test_results.append(("Application Start", False))
        print("⚠️  Application startup test had issues")
    
    # Generate deployment package
    if generate_deployment_package():
        test_results.append(("Deployment Package", True))
    else:
        test_results.append(("Deployment Package", False))
        print("❌ Failed to generate deployment package")
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
        print("\nNext steps:")
        print("1. Transfer crypto-scanner-ai-advisor.tar.gz to Linux server")
        print("2. Run deploy-linux.sh on the server")
        print("3. Start with docker-compose up -d")
    else:
        print("⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
