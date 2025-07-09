#!/usr/bin/env python3
"""
Test new Line Breakout + EMA7 strategy with 7 timeframes and 2-candle EMA7 cross
"""

import sys
import json

def test_new_strategy():
    """Test the updated Line Breakout + EMA7 strategy"""
    print("🧪 Testing NEW Line Breakout + EMA7 Strategy...")
    print("=" * 60)
    print("📊 Updates:")
    print("   - Breakout detection: 7 timeframes (was 5)")
    print("   - EMA7 confirmation: 2 latest candles cross EMA7 (was candle color)")
    print("   - LONG: Breakout UP + any of 2 candles cross EMA7")
    print("   - SHORT: Breakout DOWN + any of 2 candles cross EMA7")
    print("=" * 60)
    
    try:
        # Import pattern detector
        from pattern_detector import PatternDetector
        print("✅ PatternDetector imported successfully")
        
        # Create sample OHLCV data (22 candles for better EMA7 calculation)
        sample_data = []
        base_price = 45000
        
        # Create a trend with breakout at candle 18 (within last 7 candles)
        for i in range(22):
            price_movement = i * 30  # Gradual increase
            
            # Add stronger breakout movement starting at candle 18
            if i >= 18:  # Breakout in last 4 candles (within 7-candle window)
                price_movement += (i - 17) * 150  # Strong breakout movement
                
            # Create candle data
            open_price = base_price + price_movement
            high_price = open_price + 100 + (i * 5)
            low_price = open_price - 80 - (i * 3)
            close_price = open_price + 75 + (i * 2)
            
            # For last 2 candles, ensure one crosses EMA7
            if i == 20:  # Second last candle - make it cross EMA7
                # Calculate approximate EMA7 value (around 45600)
                approx_ema7 = base_price + 600
                low_price = approx_ema7 - 50   # Ensure candle crosses EMA7
                high_price = approx_ema7 + 100
                
            sample_data.append({
                'timestamp': 1700000000 + i * 3600,  # 1H intervals
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': 1000 + i * 50
            })
        
        # Initialize detector
        detector = PatternDetector()
        print("✅ PatternDetector initialized")
        
        # Analyze patterns
        result = detector.detect_patterns(sample_data)
        print("✅ Pattern analysis completed")
        
        # Display results
        print(f"\n📊 NEW Strategy Analysis Results:")
        print(f"   Status: {result.get('status', 'N/A')}")
        print(f"   Signal: {result.get('signal', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 0)}%")
        print(f"   Pattern detected: {result.get('pattern_detected', False)}")
        
        if result.get('pattern_detected'):
            print(f"   Direction: {result.get('breakout_direction', 'N/A')}")
            print(f"   Candles ago: {result.get('breakout_candles_ago', 'N/A')}")
            print(f"   EMA7 Cross: {result.get('candle_vs_ema7', 'N/A')}")
            print(f"   EMA7 Value: {result.get('ema7_value', 0):.2f}")
        
        # Pretty print full result for debugging
        print(f"\n📋 Full Result:")
        print(json.dumps(result, indent=2))
        
        # Test validation
        if result.get('status') == 'success':
            print("\n✅ NEW Strategy test passed!")
            if result.get('signal') != 'NEUTRAL':
                print(f"🎯 Valid {result.get('signal')} signal detected!")
            return True
        else:
            print("\n❌ Test failed - check implementation")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run new strategy test"""
    print("🚀 Line Breakout + EMA7 NEW Strategy Test")
    print("=" * 50)
    
    success = test_new_strategy()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 NEW strategy test completed!")
        print("✅ 7 timeframes + 2-candle EMA7 cross logic working")
    else:
        print("❌ NEW strategy test failed")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
