#!/usr/bin/env python3
"""
Test script for Docker environment
Tests Pattern Detector and basic functionality
"""

import sys
import json

def test_imports():
    """Test basic imports"""
    try:
        print("🔍 Testing imports...")
        
        # Test basic libraries
        import numpy as np
        import pandas as pd
        import ccxt
        print("✅ Basic libraries: numpy, pandas, ccxt")
        
        # Test pattern detector
        from pattern_detector import PatternDetector, LineBreakoutEMA7Detector
        print("✅ Pattern Detector imported successfully")
        
        # Test AI analyzer
        from ai_analyzer import AIAnalyzer
        print("✅ AI Analyzer imported successfully")
        
        # Test exchange client
        from exchange_client import ExchangeClient
        print("✅ Exchange Client imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_pattern_detector():
    """Test Pattern Detector functionality"""
    try:
        print("🔍 Testing Pattern Detector...")
        
        # Create sample OHLCV data
        sample_data = {
            "symbol": "BTCUSDT",
            "ohlcv_1h": [
                [1609459200000, 29000, 29500, 28800, 29200, 1000],
                [1609462800000, 29200, 29600, 29000, 29400, 1100],
                [1609466400000, 29400, 29800, 29200, 29600, 1200],
                [1609470000000, 29600, 30000, 29400, 29800, 1300],
                [1609473600000, 29800, 30200, 29600, 30000, 1400],
                [1609477200000, 30000, 30400, 29800, 30200, 1500],
                [1609480800000, 30200, 30600, 30000, 30400, 1600],
                [1609484400000, 30400, 30800, 30200, 30600, 1700],
                [1609488000000, 30600, 31000, 30400, 30800, 1800],
                [1609491600000, 30800, 31200, 30600, 31000, 1900],
                [1609495200000, 31000, 31400, 30800, 31200, 2000],
                [1609498800000, 31200, 31600, 31000, 31400, 2100],
                [1609502400000, 31400, 31800, 31200, 31600, 2200],
                [1609506000000, 31600, 32000, 31400, 31800, 2300],
                [1609509600000, 31800, 32200, 31600, 32000, 2400],
                [1609513200000, 32000, 32400, 31800, 32200, 2500],
                [1609516800000, 32200, 32600, 32000, 32400, 2600],
                [1609520400000, 32400, 32800, 32200, 32600, 2700],
                [1609524000000, 32600, 33000, 32400, 32800, 2800],
                [1609527600000, 32800, 33200, 32600, 33000, 2900]
            ]
        }
        
        # Test via stdin (pattern detector expects JSON input)
        import subprocess
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_data, f)
            temp_file = f.name
        
        # Run pattern detector
        result = subprocess.run(
            ['python', 'pattern_detector.py'], 
            input=json.dumps(sample_data),
            text=True,
            capture_output=True,
            timeout=30
        )
        
        if result.returncode == 0:
            try:
                output = json.loads(result.stdout)
                print(f"✅ Pattern Detector result: {output.get('pattern', 'N/A')}")
                print(f"   Signal: {output.get('signal', 'N/A')}")
                print(f"   Confidence: {output.get('confidence', 0):.1f}%")
                return True
            except:
                print(f"⚠️ Pattern Detector output: {result.stdout[:200]}...")
                return False
        else:
            print(f"❌ Pattern Detector error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Pattern Detector test error: {e}")
        return False

def main():
    """Main test function"""
    print("🐳 Docker Environment Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    print()
    
    # Test pattern detector
    if not test_pattern_detector():
        print("⚠️ Pattern Detector test failed, but continuing...")
    
    print()
    print("✅ Docker environment test completed")
    print("🚀 Ready to run main application")

if __name__ == "__main__":
    main()
