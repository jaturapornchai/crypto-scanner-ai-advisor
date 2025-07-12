#!/usr/bin/env python3
"""
Test AI Analyzer with Wide Channel for Better Risk-Reward
ทดสอบ AI กับ channel ที่กว้างขึ้นเพื่อให้ได้ Risk-Reward ที่ดีกว่า
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_analyzer import AIAnalyzer
import json

def create_wide_channel_ohlcv():
    """สร้างข้อมูล OHLCV ที่มี channel กว้างขึ้นเพื่อให้ AI ทำ Risk-Reward ที่ดีกว่า"""
    base_data = []
    
    # สร้างข้อมูล 100 แท่งแรกที่มี channel กว้าง (volatility สูง)
    base_price = 45000.0
    for i in range(100):
        # Channel กว้างขึ้น - volatility สูงขึ้น
        price_variation = (i % 20 - 10) * 200  # variation ±2000 (กว้างขึ้น 4 เท่า)
        
        timestamp = 1640995200000 + (i * 3600000)
        open_price = base_price + price_variation
        high = open_price + 800  # กว้างขึ้น
        low = open_price - 800   # กว้างขึ้น
        close = open_price + ((i % 3) - 1) * 400  # กว้างขึ้น
        volume = 1000000 + (i % 1000) * 1000
        
        base_data.append([timestamp, open_price, high, low, close, volume])
    
    # เพิ่ม 20 แท่งที่แสดง strong breakout จาก wide channel
    for i in range(100, 120):
        if i >= 117:  # แท่งที่ 3 ล่าสุด - Very strong breakout
            timestamp = 1640995200000 + (i * 3600000)
            open_price = 47000 + ((i - 117) * 800)  # Strong breakout upward
            high = open_price + 1200
            low = open_price - 300
            close = open_price + 1000  # Very strong close
            volume = 3000000 + ((i - 117) * 800000)  # High volume spike
        else:
            timestamp = 1640995200000 + (i * 3600000)
            open_price = 45000 + ((i - 100) * 100)
            high = open_price + 500
            low = open_price - 500
            close = open_price + ((i % 2) * 200)
            volume = 1500000
        
        base_data.append([timestamp, open_price, high, low, close, volume])
    
    return base_data

def test_wide_channel():
    """ทดสอบกับ wide channel เพื่อดู Risk-Reward ที่ดีขึ้น"""
    
    print("🧪 ทดสอบ AI Analyzer - Wide Channel for Better Risk-Reward")
    print("=" * 70)
    
    try:
        ai_analyzer = AIAnalyzer()
        
        # สร้างข้อมูล wide channel
        ohlcv_1h = create_wide_channel_ohlcv()
        
        patterns = [
            {
                "type": "Linear Regression Channel",
                "signal": "STRONG_BREAKOUT_UP",
                "trend_direction": "strong_uptrend",
                "breakout_candles_ago": 2,
                "confidence": 92,
                "pattern_status": "CONFIRMED"
            }
        ]
        
        print(f"📊 ราคาปัจจุบัน: {ohlcv_1h[-1][4]:.2f} USDT")
        print(f"📈 Channel Range: {min([c[3] for c in ohlcv_1h[-20:]]):.0f} - {max([c[2] for c in ohlcv_1h[-20:]]):.0f}")
        
        # วิเคราะห์
        result = ai_analyzer.analyze_symbol(
            symbol="BTCUSDT",
            ohlcv_1h=ohlcv_1h,
            previous_patterns=patterns
        )
        
        print("\n📋 ผลการวิเคราะห์ Wide Channel:")
        print("=" * 50)
        
        action = result.get('action', 'HOLD')
        confidence = result.get('confidence', 0)
        entry_price = result.get('entry_price', 0)
        stop_loss = result.get('stop_loss', 0)
        take_profit = result.get('take_profit', 0)
        risk_reward_ratio = result.get('risk_reward_ratio', 0)
        
        print(f"🎯 Action: {action}")
        print(f"💯 Confidence: {confidence}%")
        print(f"💰 Entry: {entry_price:.2f} USDT")
        print(f"🛑 Stop Loss: {stop_loss:.2f} USDT")
        print(f"🎯 Take Profit: {take_profit:.2f} USDT")
        print(f"📊 Risk-Reward: {risk_reward_ratio:.2f}:1")
        
        if action != "HOLD" and entry_price > 0:
            if action == "LONG":
                loss_risk = abs(entry_price - stop_loss)
                profit_potential = abs(take_profit - entry_price)
                sl_pct = (loss_risk / entry_price) * 100
                tp_pct = (profit_potential / entry_price) * 100
            
            print(f"\n📊 Risk Management Analysis:")
            print(f"   💸 Loss Risk: {loss_risk:.2f} USDT ({sl_pct:.2f}%)")
            print(f"   💰 Profit: {profit_potential:.2f} USDT ({tp_pct:.2f}%)")
            
            print(f"\n✅ Risk Management Evaluation:")
            if sl_pct <= 1.5:
                print(f"   🎯 Stop Loss: {sl_pct:.2f}% (ดีเยี่ยม - ความเสี่ยงต่ำมาก)")
            elif sl_pct <= 3.0:
                print(f"   ✅ Stop Loss: {sl_pct:.2f}% (ดี - ความเสี่ยงปานกลาง)")
            else:
                print(f"   ⚠️  Stop Loss: {sl_pct:.2f}% (สูง)")
                
            if tp_pct >= 8.0:
                print(f"   🚀 Take Profit: {tp_pct:.2f}% (ดีเยี่ยม - โอกาสกำไรสูงมาก)")
            elif tp_pct >= 5.0:
                print(f"   ✅ Take Profit: {tp_pct:.2f}% (ดี - โอกาสกำไรดี)")
            else:
                print(f"   📉 Take Profit: {tp_pct:.2f}% (ต่ำ)")
                
            if risk_reward_ratio >= 3.0:
                print(f"   💯 Risk-Reward: {risk_reward_ratio:.2f}:1 (ผ่านเกณฑ์)")
            else:
                print(f"   ❌ Risk-Reward: {risk_reward_ratio:.2f}:1 (ไม่ผ่านเกณฑ์)")
        
        print(f"\n📝 Analysis: {result.get('analysis', 'No analysis')}")
        
        print(f"\n{'='*70}")
        if action == "HOLD":
            print("❌ Wide Channel ยังไม่เพียงพอ - ต้องการ channel ที่กว้างกว่านี้")
            print("💡 ข้อเสนอแนะ: ปรับเกณฑ์หา channel ที่มี volatility สูงกว่า")
        else:
            print(f"✅ Wide Channel ให้ผลลัพธ์ที่ดี - {action} signal")
            print(f"🎯 Risk-Reward: {risk_reward_ratio:.2f}:1")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_wide_channel()
