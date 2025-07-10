#!/usr/bin/env python3
from linear_regression_detector import LinearRegressionChannelDetector, OHLCV

def test_take_profit_validation():
    """Test take profit validation logic"""
    print("🧪 Testing Take Profit Validation Logic")
    print("=" * 50)
    
    # สร้าง mock data สำหรับทดสอบ
    symbol = "ADAUSDT" 
    
    # Mock OHLCV data
    mock_ohlcv = []
    base_price = 0.000460
    for i in range(120):
        # สร้างข้อมูลจำลองที่มี breakout pattern
        price = base_price + (i * 0.000001) + (0.000005 if i % 2 == 0 else -0.000005)
        ohlcv = OHLCV(
            timestamp=1640995200000 + i * 3600000,  # timestamp
            open=price * 0.999,      # open
            high=price * 1.002,      # high
            low=price * 0.998,       # low
            close=price,             # close
            volume=1000000           # volume
        )
        mock_ohlcv.append(ohlcv)
    
    print(f"📊 Created mock OHLCV data for {symbol}")
    print(f"📊 Current price (last close): {mock_ohlcv[-1].close:.6f}")
    
    # สร้าง detector
    detector = LinearRegressionChannelDetector(data=mock_ohlcv)
    
    try:
        # ทดสอบ LRC + EMA7 detection
        result = detector.detect_breakout_with_ema7_confirmation(max_lookback=10)
        
        if result:
            print(f"\n✅ LRC + EMA7 Detection Result:")
            print(f"    Signal: {result.signal}")
            print(f"    Pattern: {result.pattern_type}")
            print(f"    Confidence: {result.confidence}%")
            print(f"    Entry Level: {result.entry_level:.6f}")
            print(f"    Stop Loss: {result.stop_loss:.6f}")
            print(f"    Take Profit: {result.take_profit:.6f}")
            print(f"    Current Price: {mock_ohlcv[-1].close:.6f}")
            
            # ตรวจสอบ validation
            current_price = mock_ohlcv[-1].close
            if result.signal == "LONG":
                print(f"\n🔍 LONG Position Validation:")
                print(f"    Take Profit > Current Price? {result.take_profit:.6f} > {current_price:.6f} = {result.take_profit > current_price}")
                print(f"    Stop Loss < Current Price? {result.stop_loss:.6f} < {current_price:.6f} = {result.stop_loss < current_price}")
                
                if result.take_profit <= current_price:
                    print(f"    ❌ VALIDATION FAILED: Take Profit {result.take_profit:.6f} <= Current Price {current_price:.6f}")
                else:
                    print(f"    ✅ VALIDATION PASSED")
                    
            elif result.signal == "SHORT":
                print(f"\n🔍 SHORT Position Validation:")
                print(f"    Take Profit < Current Price? {result.take_profit:.6f} < {current_price:.6f} = {result.take_profit < current_price}")
                print(f"    Stop Loss > Current Price? {result.stop_loss:.6f} > {current_price:.6f} = {result.stop_loss > current_price}")
                
                if result.take_profit >= current_price:
                    print(f"    ❌ VALIDATION FAILED: Take Profit {result.take_profit:.6f} >= Current Price {current_price:.6f}")
                else:
                    print(f"    ✅ VALIDATION PASSED")
        else:
            print("❌ No signal detected")
            
    except Exception as e:
        print(f"❌ Error during detection: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_take_profit_validation()
