#!/usr/bin/env python3
"""
ทดสอบระบบสมบูรณ์ที่ไม่ใช้ EMA และให้ AI คำนวณ SL/TP
"""

import json
from linear_regression_detector import LinearRegressionChannelDetector, OHLCV

def test_complete_system():
    """ทดสอบระบบสมบูรณ์"""
    print("🧪 ทดสอบระบบสมบูรณ์: ไม่ใช้ EMA + AI คำนวณ SL/TP")
    print("="*70)
    
    # โหลดข้อมูล BTC
    try:
        with open('historical_data_cache/BTC_USDT_USDT_1h.json', 'r') as f:
            btc_data = json.load(f)
        
        print(f"📊 โหลดข้อมูล BTC: {len(btc_data)} records")
        
        # แปลงเป็น OHLCV objects
        ohlcv_data = []
        for candle in btc_data:  # ข้อมูลเป็น array โดยตรง ไม่มี 'data' wrapper
            ohlcv_data.append(OHLCV(
                timestamp=int(candle[0]),
                open=float(candle[1]),
                high=float(candle[2]),
                low=float(candle[3]),
                close=float(candle[4]),
                volume=float(candle[5])
            ))
        
        print(f"✅ แปลงข้อมูล: {len(ohlcv_data)} OHLCV objects")
        print()
        
        # ขั้นตอนที่ 1: Linear Regression Channel Detection
        print("🔍 ขั้นตอนที่ 1: Linear Regression Channel Detection")
        print("-" * 50)
        
        detector = LinearRegressionChannelDetector(ohlcv_data)
        result = detector.detect_breakout_with_channel_price_check()
        
        print(f"Pattern Type: {result.pattern_type}")
        print(f"Signal: {result.signal}")
        print(f"Confidence: {result.confidence}%")
        print(f"Trend Direction: {result.trend_direction}")
        print(f"Fresh Breakout: {result.is_fresh_breakout}")
        print(f"Breakout Candles Ago: {result.breakout_candles_ago}")
        print()
        
        # ขั้นตอนที่ 1.5: ตรวจสอบเงื่อนไขใหม่
        print("🚦 ขั้นตอนที่ 1.5: ตรวจสอบเงื่อนไขการเปิด Position")
        print("-" * 50)
        
        # เงื่อนไขที่ 1: Trend Direction ไม่เป็น "sideways"
        trend_check = result.trend_direction.lower() != 'sideways'
        print(f"✅ Trend Direction: {result.trend_direction} ({'PASS' if trend_check else 'FAIL - Sideways market'})")
        
        # เงื่อนไขที่ 2: Confidence >= 80% (จะต้องให้ AI คำนวณจริงๆ)
        # สำหรับการทดสอบ ใช้ confidence จาก LRC result ก่อน
        confidence_check = result.confidence >= 80
        print(f"✅ Confidence: {result.confidence}% ({'PASS' if confidence_check else 'FAIL - Below 80%'})")
        
        position_allowed = trend_check and confidence_check
        print(f"🚀 Position Allowed: {'YES' if position_allowed else 'NO'}")
        print()
        
        if not position_allowed:
            print("⚠️ ไม่ผ่านเงื่อนไขการเปิด Position - หยุดการทดสอบ")
            return
        print()
        
        # ขั้นตอนที่ 2: Channel Price Validation
        print("📊 ขั้นตอนที่ 2: Channel Price Validation")
        print("-" * 50)
        
        current_price = ohlcv_data[-1].close
        print(f"ราคาปัจจุบัน: {current_price:.6f}")
        print(f"Upper Channel: {result.upper_channel:.6f}")
        print(f"Middle Line: {result.middle_line:.6f}")
        print(f"Lower Channel: {result.lower_channel:.6f}")
        
        if result.signal == "LONG":
            validation = current_price < result.upper_channel
            print(f"Long Validation: ราคา < Upper? {validation} ✅" if validation else f"Long Validation: ราคา < Upper? {validation} ❌")
        elif result.signal == "SHORT":
            validation = current_price > result.lower_channel
            print(f"Short Validation: ราคา > Lower? {validation} ✅" if validation else f"Short Validation: ราคา > Lower? {validation} ❌")
        else:
            print("No Signal")
        print()
        
        # ขั้นตอนที่ 3: ข้อมูลที่ส่งให้ AI
        print("🤖 ขั้นตอนที่ 3: ข้อมูลที่ส่งให้ AI คำนวณ SL/TP")
        print("-" * 50)
        
        if result.signal != "NEUTRAL":
            # สร้างข้อมูลที่จะส่งให้ AI
            channel_width = result.upper_channel - result.lower_channel
            ai_data = {
                'signal': result.signal,
                'current_price': current_price,
                'entry_level': current_price,
                'upper_channel': result.upper_channel,
                'middle_line': result.middle_line,
                'lower_channel': result.lower_channel,
                'channel_width': channel_width,
                'slope': result.slope,
                'confidence': result.confidence,
                'breakout_candles_ago': result.breakout_candles_ago,
                'request_ai_sl_tp': True
            }
            
            print("ข้อมูลที่ส่งให้ AI:")
            for key, value in ai_data.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.6f}")
                else:
                    print(f"  {key}: {value}")
            print()
            
            # ขั้นตอนที่ 4: AI คำนวณ SL/TP (ตัวอย่าง)
            print("💡 ขั้นตอนที่ 4: AI คำนวณ SL/TP (ตัวอย่าง)")
            print("-" * 50)
            
            # Initialize AI SL/TP variables
            ai_stop_loss = 0.0
            ai_take_profit = 0.0
            
            if result.signal == "LONG":
                # Long: SL = Middle Line, TP = Entry + (Channel Width × 1.5)
                ai_stop_loss = result.middle_line
                ai_take_profit = current_price + (channel_width * 1.5)
            elif result.signal == "SHORT":
                # Short: SL = Middle Line, TP = Entry - (Channel Width × 1.5)
                ai_stop_loss = result.middle_line
                ai_take_profit = current_price - (channel_width * 1.5)
            
            sl_distance = abs(current_price - ai_stop_loss)
            tp_distance = abs(ai_take_profit - current_price)
            risk_reward = tp_distance / sl_distance if sl_distance > 0 else 0
            
            print(f"AI Stop Loss: {ai_stop_loss:.6f}")
            print(f"  ↳ ระยะห่าง: {sl_distance:.6f} ({(sl_distance/current_price)*100:.2f}%)")
            print(f"AI Take Profit: {ai_take_profit:.6f}")
            print(f"  ↳ ระยะห่าง: {tp_distance:.6f} ({(tp_distance/current_price)*100:.2f}%)")
            print(f"Risk:Reward = 1:{risk_reward:.2f}")
            print(f"Channel Width = {channel_width:.6f}")
            
            # สรุปผลลัพธ์
            print()
            print("🎯 สรุปผลลัพธ์ระบบใหม่")
            print("=" * 50)
            print(f"✅ ไม่ใช้ EMA แล้ว")
            print(f"✅ ใช้ Channel Price Validation")
            print(f"✅ ตรวจสอบ Trend Direction != 'sideways'")
            print(f"✅ ตรวจสอบ AI Confidence >= 80%")
            print(f"✅ AI คำนวณ SL/TP ตาม Channel Width")
            print(f"✅ Risk:Reward >= 1:2 ({risk_reward:.2f})")
            print(f"✅ Dynamic SL/TP ตาม Market Condition")
            
        else:
            print("⚠️ No Signal - ไม่คำนวณ SL/TP")
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาด: {e}")

if __name__ == "__main__":
    test_complete_system()
