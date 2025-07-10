#!/usr/bin/env python3
"""
ทดสอบระบบใหม่ที่ให้ AI คำนวณ Stop Loss และ Take Profit
"""

import json
from linear_regression_detector import LinearRegressionChannelDetector, OHLCV, ensure_all_required_folders

def test_ai_sl_tp_system():
    """ทดสอบระบบใหม่ที่ AI คำนวณ SL/TP"""
    print("🧪 ทดสอบระบบ AI คำนวณ SL/TP")
    print("="*60)
    
    # ใช้ระบบ auto-folders และ cache
    cache_file = ensure_all_required_folders()
    print(f"📂 ใช้ไฟล์: {cache_file}")
    print("📁 ตรวจสอบโครงสร้างโฟลเดอร์เรียบร้อย")
    print("="*60)
    
    # โหลดข้อมูล BTC
    try:
        with open(cache_file, 'r') as f:
            btc_data = json.load(f)
        
        print(f"📊 โหลดข้อมูล BTC: {len(btc_data)} records")
        
        # แปลงข้อมูลเป็น OHLCV objects
        ohlcv_data = []
        for candle in btc_data:
            ohlcv_data.append(OHLCV(
                timestamp=int(candle[0]),
                open=float(candle[1]),
                high=float(candle[2]),
                low=float(candle[3]),
                close=float(candle[4]),
                volume=float(candle[5])
            ))
        
        print(f"✅ แปลงข้อมูล: {len(ohlcv_data)} OHLCV objects")
        
        # ใช้ LRC detector
        detector = LinearRegressionChannelDetector(ohlcv_data)
        result = detector.detect_breakout_with_channel_price_check()
        
        print(f"\n📊 ผลลัพธ์ LRC Detection:")
        print("="*40)
        print(f"Pattern Type: {result.pattern_type}")
        print(f"Signal: {result.signal}")
        print(f"Confidence: {result.confidence}%")
        print(f"Entry Level: {result.entry_level}")
        print(f"Stop Loss: {result.stop_loss} (AI จะคำนวณใหม่)")
        print(f"Take Profit: {result.take_profit} (AI จะคำนวณใหม่)")
        print(f"Upper Channel: {result.upper_channel}")
        print(f"Lower Channel: {result.lower_channel}")
        print(f"Middle Line: {result.middle_line}")
        print(f"Channel Width: {result.upper_channel - result.lower_channel}")
        
        if result.signal != "NEUTRAL":
            print(f"\n🤖 ข้อมูลที่ส่งให้ AI คำนวณ SL/TP:")
            print("="*40)
            print(f"Signal: {result.signal}")
            print(f"Current Price: {result.entry_level}")
            print(f"Entry Level: {result.entry_level}")
            print(f"Upper Channel: {result.upper_channel}")
            print(f"Middle Line: {result.middle_line}")
            print(f"Lower Channel: {result.lower_channel}")
            print(f"Channel Width: {result.upper_channel - result.lower_channel}")
            print(f"Slope: {result.slope}")
            
            # จำลอง AI คำนวณ SL/TP
            channel_width = result.upper_channel - result.lower_channel
            if result.signal == "LONG":
                ai_stop_loss = result.middle_line  # ใช้ middle line เป็น SL
                ai_take_profit = result.entry_level + (channel_width * 1.5)  # 1.5x channel width
            else:
                ai_stop_loss = result.middle_line  # ใช้ middle line เป็น SL
                ai_take_profit = result.entry_level - (channel_width * 1.5)  # 1.5x channel width
            
            distance_sl = abs(result.entry_level - ai_stop_loss)
            distance_tp = abs(ai_take_profit - result.entry_level)
            risk_reward = distance_tp / distance_sl if distance_sl > 0 else 0
            
            print(f"\n💡 AI คำนวณ SL/TP ที่เหมาะสม:")
            print("="*40)
            print(f"Stop Loss: {ai_stop_loss} (ระยะ: {distance_sl} = {(distance_sl/result.entry_level)*100:.2f}%)")
            print(f"Take Profit: {ai_take_profit} (ระยะ: {distance_tp} = {(distance_tp/result.entry_level)*100:.2f}%)")
            print(f"Risk:Reward = 1:{risk_reward:.2f}")
            print(f"Channel-based calculation: ใช้ Channel Width {channel_width}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ai_sl_tp_system()
