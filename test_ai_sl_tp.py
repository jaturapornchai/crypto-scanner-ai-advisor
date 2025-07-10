#!/usr/bin/env python3        # แปลงข้อมูลเป็น OHLCV objects
        ohlcv_data = []
        for candle in btc_data:  # แก้ไขจาก btc_data['data'] เป็น btc_data
            ohlcv_data.append(OHLCV(
                timestamp=int(candle[0]),
                open=float(candle[1]),
                high=float(candle[2]),
                low=float(candle[3]),
                close=float(candle[4]),
                volume=float(candle[5])
            ))ระบบใหม่ที่ให้ AI คำนวณ Stop Loss และ Take Profit
"""

import json
from linear_regression_detector import LinearRegressionChannelDetector, OHLCV, ensure_historical_data_cache

def test_ai_sl_tp_system():
    """ทดสอบระบบใหม่ที่ AI คำนวณ SL/TP"""
    print("🧪 ทดสอบระบบ AI คำนวณ SL/TP")
    print("="*60)
    
    # ใช้ระบบ auto-cache
    cache_file = ensure_historical_data_cache()
    
    # โหลดข้อมูล BTC
    try:
        with open(cache_file, 'r') as f:
            btc_data = json.load(f)
        
        print(f"📊 โหลดข้อมูล BTC: {len(btc_data)} records")
        
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
        
        print(f"\n📊 ผลลัพธ์ LRC Detection:")
        print(f"="*40)
        print(f"Pattern Type: {result.pattern_type}")
        print(f"Signal: {result.signal}")
        print(f"Confidence: {result.confidence}%")
        print(f"Entry Level: {result.entry_level:.6f}")
        print(f"Stop Loss: {result.stop_loss:.6f} (AI จะคำนวณใหม่)")
        print(f"Take Profit: {result.take_profit:.6f} (AI จะคำนวณใหม่)")
        print(f"Upper Channel: {result.upper_channel:.6f}")
        print(f"Lower Channel: {result.lower_channel:.6f}")
        print(f"Middle Line: {result.middle_line:.6f}")
        print(f"Channel Width: {result.upper_channel - result.lower_channel:.6f}")
        
        # แสดงข้อมูลที่จะส่งให้ AI
        current_price = ohlcv_data[-1].close
        channel_width = result.upper_channel - result.lower_channel
        
        print(f"\n🤖 ข้อมูลที่ส่งให้ AI คำนวณ SL/TP:")
        print(f"="*40)
        print(f"Signal: {result.signal}")
        print(f"Current Price: {current_price:.6f}")
        print(f"Entry Level: {current_price:.6f}")
        print(f"Upper Channel: {result.upper_channel:.6f}")
        print(f"Middle Line: {result.middle_line:.6f}")
        print(f"Lower Channel: {result.lower_channel:.6f}")
        print(f"Channel Width: {channel_width:.6f}")
        print(f"Slope: {result.slope:.6f}")
        
        # คำนวณ SL/TP แบบตัวอย่าง (ที่ AI จะคำนวณ)
        if result.signal == "LONG":
            # Long: SL = Middle Line หรือ Lower Channel, TP = Entry + (Channel Width × 1.5-2.0)
            suggested_sl = result.middle_line  # หรือ lower_channel ขึ้นกับ volatility
            suggested_tp = current_price + (channel_width * 1.5)
            sl_distance = abs(current_price - suggested_sl)
            tp_distance = abs(suggested_tp - current_price)
        elif result.signal == "SHORT":
            # Short: SL = Middle Line หรือ Upper Channel, TP = Entry - (Channel Width × 1.5-2.0)  
            suggested_sl = result.middle_line  # หรือ upper_channel ขึ้นกับ volatility
            suggested_tp = current_price - (channel_width * 1.5)
            sl_distance = abs(suggested_sl - current_price)
            tp_distance = abs(current_price - suggested_tp)
        else:
            suggested_sl = 0
            suggested_tp = 0
            sl_distance = 0
            tp_distance = 0
        
        if result.signal != "NEUTRAL":
            risk_reward = tp_distance / sl_distance if sl_distance > 0 else 0
            
            print(f"\n💡 AI คำนวณ SL/TP ที่เหมาะสม:")
            print(f"="*40)
            print(f"Stop Loss: {suggested_sl:.6f} (ระยะ: {sl_distance:.6f} = {(sl_distance/current_price)*100:.2f}%)")
            print(f"Take Profit: {suggested_tp:.6f} (ระยะ: {tp_distance:.6f} = {(tp_distance/current_price)*100:.2f}%)")
            print(f"Risk:Reward = 1:{risk_reward:.2f}")
            print(f"Channel-based calculation: ใช้ Channel Width {channel_width:.6f}")
        else:
            print(f"\n⚠️ No Signal - ไม่คำนวณ SL/TP")
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาด: {e}")

if __name__ == "__main__":
    test_ai_sl_tp_system()
