#!/usr/bin/env python3
"""Test the LRC + EMA7 take profit validation specifically"""

from linear_regression_detector import LinearRegressionChannelDetector, OHLCV

def test_specific_scenario():
    """Test the exact scenario from the error"""
    print("🧪 Testing Specific LRC EMA7 Take Profit Validation")
    print("=" * 60)
    
    # Create mock data that simulates the NEIRO/USDT scenario
    current_price = 0.000460
    upper_channel = 0.000444  # from log: upper channel lower than current price
    
    # Create mock OHLCV data to simulate an UP breakout in downtrend
    mock_data = []
    for i in range(120):
        # Create a downtrend with breakout
        if i < 100:
            # Downtrend
            price = 0.000500 - (i * 0.000001)
        else:
            # Recent UP breakout
            price = current_price + (i - 100) * 0.000001
            
        ohlcv = OHLCV(
            timestamp=1640995200000 + i * 3600000,
            open=price * 0.9995,
            high=price * 1.001,
            low=price * 0.999,
            close=price,
            volume=1000000
        )
        mock_data.append(ohlcv)
    
    # Override the last candle to match the scenario
    mock_data[-1] = OHLCV(
        timestamp=mock_data[-1].timestamp,
        open=current_price * 0.999,
        high=current_price * 1.001,
        low=current_price * 0.998,
        close=current_price,
        volume=1000000
    )
    
    print(f"📊 Simulated scenario:")
    print(f"    Current price: {current_price:.6f}")
    print(f"    Expected upper channel: ~{upper_channel:.6f}")
    print(f"    Scenario: UP breakout in downtrend")
    
    # Test with detector
    detector = LinearRegressionChannelDetector(data=mock_data)
    result = detector.detect_breakout_with_ema7_confirmation(max_lookback=10)
    
    if result and result.signal != "NEUTRAL":
        print(f"\n✅ LRC + EMA7 Detection Result:")
        print(f"    Signal: {result.signal}")
        print(f"    Pattern: {result.pattern_type}")
        print(f"    Confidence: {result.confidence}%")
        print(f"    Current Price: {current_price:.10f}")
        print(f"    Stop Loss (EMA7): {result.stop_loss:.10f}")
        print(f"    Take Profit: {result.take_profit:.10f}")
        print(f"    Upper Channel: {result.upper_channel:.10f}")
        print(f"    Lower Channel: {result.lower_channel:.10f}")
        
        # Validation check
        if result.signal == "LONG":
            print(f"\n🔍 LONG Position Validation:")
            valid_tp = result.take_profit > current_price
            valid_sl = result.stop_loss < current_price
            print(f"    TP > Current? {result.take_profit:.10f} > {current_price:.10f} = {valid_tp}")
            print(f"    SL < Current? {result.stop_loss:.10f} < {current_price:.10f} = {valid_sl}")
            
            if valid_tp and valid_sl:
                print(f"    ✅ VALIDATION PASSED - Ready for trading")
            else:
                print(f"    ❌ VALIDATION FAILED")
                if not valid_tp:
                    print(f"        - Take profit too low!")
                if not valid_sl:
                    print(f"        - Stop loss too high!")
        
        elif result.signal == "SHORT":
            print(f"\n🔍 SHORT Position Validation:")
            valid_tp = result.take_profit < current_price
            valid_sl = result.stop_loss > current_price
            print(f"    TP < Current? {result.take_profit:.10f} < {current_price:.10f} = {valid_tp}")
            print(f"    SL > Current? {result.stop_loss:.10f} > {current_price:.10f} = {valid_sl}")
            
            if valid_tp and valid_sl:
                print(f"    ✅ VALIDATION PASSED - Ready for trading")
            else:
                print(f"    ❌ VALIDATION FAILED")
    else:
        print(f"\n❌ No valid signal detected")
        if result:
            print(f"    Signal: {result.signal}")
            print(f"    Pattern: {result.pattern_type}")

if __name__ == "__main__":
    test_specific_scenario()
