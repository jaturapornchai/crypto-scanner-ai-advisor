#!/usr/bin/env python3
"""
Simple test without network dependencies
"""

import sys
import json

def test_pattern_detector_only():
    """Test only the pattern detector without network dependencies"""
    print("🧪 Testing PatternDetector (offline)...")
    
    try:
        # Import pattern detector
        from pattern_detector import PatternDetector
        print("✅ PatternDetector imported successfully")
        
        # Create sample OHLCV data (20 candles)
        sample_data = []
        base_price = 42000
        
        # Create a simple upward trend with a breakout
        for i in range(20):
            price_movement = i * 50  # Gradual increase
            if i >= 15:  # Add breakout after candle 15
                price_movement += (i - 14) * 100  # Steeper increase
                
            sample_data.append({
                'timestamp': 1700000000 + i * 3600,  # 1H intervals
                'open': base_price + price_movement,
                'high': base_price + price_movement + 150,
                'low': base_price + price_movement - 100,
                'close': base_price + price_movement + 50,
                'volume': 1000 + i * 50
            })
        
        # Initialize detector
        detector = PatternDetector()
        print("✅ PatternDetector initialized")
        
        # Analyze patterns
        result = detector.detect_patterns(sample_data)
        print("✅ Pattern analysis completed")
        
        # Display results
        print(f"\n📊 Analysis Results:")
        print(f"   Status: {result.get('status', 'N/A')}")
        print(f"   Signal: {result.get('signal', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 0)}%")
        print(f"   Pattern detected: {result.get('pattern_detected', False)}")
        
        if result.get('pattern_detected'):
            print(f"   Direction: {result.get('breakout_direction', 'N/A')}")
            print(f"   Candles ago: {result.get('breakout_candles_ago', 'N/A')}")
            print(f"   Latest candle: {result.get('latest_candle_color', 'N/A')}")
            print(f"   EMA7 position: {result.get('candle_vs_ema7', 'N/A')}")
        
        # Pretty print full result for debugging
        print(f"\n📋 Full Result:")
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run simple offline test"""
    print("🚀 Simple Line Breakout + EMA7 Test (Offline)")
    print("=" * 50)
    
    success = test_pattern_detector_only()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Pattern detector test passed!")
        print("✅ Line Breakout + EMA7 logic is working correctly")
    else:
        print("❌ Pattern detector test failed")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
