#!/usr/bin/env python3
"""
Quick deployment preparation script to ensure all files are ready for Docker build.
"""

import os
import sys

def check_dockerfile():
    """Check if Dockerfile exists and has correct content"""
    if not os.path.exists('Dockerfile'):
        print("❌ Dockerfile not found")
        return False
    
    with open('Dockerfile', 'r') as f:
        content = f.read()
    
    if 'FROM python:3.11-slim AS builder' in content:
        print("✅ Dockerfile has correct multi-stage build")
        return True
    else:
        print("❌ Dockerfile missing multi-stage build")
        return False

def check_requirements():
    """Check if requirements.txt exists"""
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    print("✅ requirements.txt found")
    return True

def check_main_files():
    """Check if main application files exist"""
    required_files = [
        'app.py',
        'enhanced_position_manager.py',
        'ai_analyzer.py',
        'linear_regression_detector.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All main application files present")
    return True

def main():
    print("🔍 Pre-deployment checks...")
    print("=" * 50)
    
    checks = [
        check_dockerfile(),
        check_requirements(), 
        check_main_files()
    ]
    
    print("=" * 50)
    
    if all(checks):
        print("🎉 All checks passed! Ready for deployment.")
        print("")
        print("📋 Quick deployment commands:")
        print("")
        print("# Local test build:")
        print("docker build --platform linux/amd64 --no-cache -t crypto-scanner-ai-advisor:test .")
        print("")
        print("# Production build and push:")
        print("docker buildx build --platform linux/amd64 --no-cache -t jaturapornchai/getspot:latest --push .")
        print("")
        print("🚀 System features:")
        print("   ✅ Hourly position/order checking")
        print("   ✅ Minimized console output")
        print("   ✅ Linear Regression Channel analysis")
        print("   ✅ AI-driven confidence calculation")
        print("   ✅ Multi-stage optimized Docker build")
    else:
        print("❌ Some checks failed. Please fix issues before deployment.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
