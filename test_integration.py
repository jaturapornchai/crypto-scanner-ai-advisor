#!/usr/bin/env python3
"""
Integration test for the new Line Breakout + EMA7 strategy
"""

import os
import sys
import traceback
from typing import Dict, Any

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from enhanced_position_manager import EnhancedPositionManager
        print("✅ EnhancedPositionManager imported")
    except Exception as e:
        print(f"❌ Failed to import EnhancedPositionManager: {e}")
        return False
    
    try:
        from exchange_client import ExchangeClient
        print("✅ ExchangeClient imported")
    except Exception as e:
        print(f"❌ Failed to import ExchangeClient: {e}")
        return False
    
    try:
        from pattern_detector import PatternDetector
        print("✅ PatternDetector imported")
    except Exception as e:
        print(f"❌ Failed to import PatternDetector: {e}")
        return False
        
    try:
        from ai_analyzer import AIAnalyzer
        print("✅ AIAnalyzer imported")
    except Exception as e:
        print(f"❌ Failed to import AIAnalyzer: {e}")
        return False
    
    return True

def test_pattern_detector():
    """Test the pattern detector with sample data"""
    print("\n🧪 Testing PatternDetector...")
    
    try:
        from pattern_detector import PatternDetector
        
        # Sample OHLCV data (20 candles for testing)
        sample_data = []
        for i in range(20):
            sample_data.append({
                'timestamp': 1700000000 + i * 3600,  # 1H intervals
                'open': 42000 + i * 10,
                'high': 42100 + i * 10,
                'low': 41900 + i * 10,
                'close': 42050 + i * 10,
                'volume': 1000 + i * 50
            })
        
        detector = PatternDetector()
        result = detector.detect_patterns(sample_data)
        
        print(f"✅ Pattern detection result: {result['status']}")
        print(f"   Signal: {result.get('signal', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 0)}")
        print(f"   Pattern detected: {result.get('pattern_detected', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern detector test failed: {e}")
        traceback.print_exc()
        return False

def test_system_initialization():
    """Test system initialization"""
    print("\n🧪 Testing system initialization...")
    
    try:
        from enhanced_position_manager import EnhancedPositionManager
        from exchange_client import ExchangeClient
        
        # Initialize exchange client
        client = ExchangeClient()
        print("✅ ExchangeClient initialized")
        
        # Initialize position manager
        manager = EnhancedPositionManager(client)
        print("✅ EnhancedPositionManager initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        traceback.print_exc()
        return False

def test_ohlcv_fetching():
    """Test OHLCV data fetching"""
    print("\n🧪 Testing OHLCV data fetching...")
    
    try:
        from enhanced_position_manager import EnhancedPositionManager
        from exchange_client import ExchangeClient
        
        client = ExchangeClient()
        manager = EnhancedPositionManager(client)
        
        # Test fetching OHLCV data
        symbol = "BTCUSDT"
        ohlcv_data = manager.get_ohlcv_data(symbol, limit=20)
        
        if ohlcv_data and len(ohlcv_data) > 0:
            print(f"✅ Fetched {len(ohlcv_data)} candles for {symbol}")
            print(f"   Latest close: {ohlcv_data[-1]['close']}")
            return True
        else:
            print("❌ No OHLCV data fetched")
            return False
            
    except Exception as e:
        print(f"❌ OHLCV fetching test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Line Breakout + EMA7 Integration Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_pattern_detector,
        test_system_initialization,
        test_ohlcv_fetching
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("⚠️ Test failed but continuing...")
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error in test: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"🏁 Integration Tests Complete: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for Line Breakout + EMA7 strategy")
    else:
        print("⚠️ Some tests failed. Please check the output above.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
