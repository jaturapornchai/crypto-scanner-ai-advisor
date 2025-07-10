#!/usr/bin/env python3
"""
ทดสอบระบบใหม่ที่ไม่ใช้ EMA แล้ว
ใช้เงื่อนไข Channel Price แทน:
- Long: ราคาอยู่ต่ำกว่าเส้นบนล่าสุด
- Short: ราคาอยู่สูงกว่าเส้นล่างล่าสุด
"""

import json
from linear_regression_detector import LinearRegressionChannelDetector, OHLCV

def test_new_system():
    """ทดสอบระบบใหม่ด้วยข้อมูล BTC"""
    print("🧪 ทดสอบระบบใหม่ที่ไม่ใช้ EMA")
    print("="*60)
    
    # โหลดข้อมูล BTC
    try:
        with open('historical_data_cache/BTC_USDT_USDT_1h.json', 'r') as f:
            btc_data = json.load(f)
        
        print(f"📊 โหลดข้อมูล BTC: {len(btc_data['data'])} records")
        
        # แปลงเป็น OHLCV objects
        ohlcv_data = []
        for candle in btc_data['data']:
            ohlcv_data.append(OHLCV(
                timestamp=int(candle[0]),
                open=float(candle[1]),
                high=float(candle[2]),
                low=float(candle[3]),
                close=float(candle[4]),
                volume=float(candle[5])
            ))
        
        print(f"✅ แปลงข้อมูล: {len(ohlcv_data)} OHLCV objects")
        
        # สร้าง detector และทดสอบ
        detector = LinearRegressionChannelDetector(ohlcv_data)
        result = detector.detect_breakout_with_channel_price_check()
        
        print(f"\n📊 ผลลัพธ์การทดสอบ:")
        print(f"="*40)
        print(f"Pattern Type: {result.pattern_type}")
        print(f"Signal: {result.signal}")
        print(f"Confidence: {result.confidence}%")
        print(f"Fresh Breakout: {result.is_fresh_breakout}")
        print(f"Entry Level: {result.entry_level:.6f}")
        print(f"Stop Loss: {result.stop_loss:.6f}")
        print(f"Take Profit: {result.take_profit:.6f}")
        print(f"Upper Channel: {result.upper_channel:.6f}")
        print(f"Lower Channel: {result.lower_channel:.6f}")
        print(f"Slope: {result.slope:.6f}")
        print(f"Breakout Candles Ago: {result.breakout_candles_ago}")
        print(f"Description: {result.description}")
        
        # แสดงราคาปัจจุบัน
        current_price = ohlcv_data[-1].close
        print(f"\n💰 ราคาปัจจุบัน: {current_price:.6f}")
        
        if result.signal == "LONG":
            print(f"📈 Long Signal: ราคา {current_price:.6f} < Upper {result.upper_channel:.6f}")
        elif result.signal == "SHORT":
            print(f"📉 Short Signal: ราคา {current_price:.6f} > Lower {result.lower_channel:.6f}")
        else:
            print(f"⚠️ No Signal")
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาด: {e}")

if __name__ == "__main__":
    test_new_system()
