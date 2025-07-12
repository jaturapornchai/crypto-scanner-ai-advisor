#!/usr/bin/env python3
"""
Test AI Analyzer with Improved Risk Management
ทดสอบ AI Analyzer ที่ปรับปรุงแล้ว:
- Stop Loss ใกล้ Entry มากขึ้น (ลดความเสี่ยง)  
- Take Profit ไกล Entry มากขึ้น (เพิ่มโอกาสกำไร)
- Risk-Reward Ratio เป็น 2.0:1 ขึ้นไป
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_analyzer import AIAnalyzer
import json

def create_sample_ohlcv_data():
    """สร้างข้อมูล OHLCV จำลองสำหรับ Linear Regression Channel breakout"""
    # สร้างข้อมูล 120 แท่งเทียนที่แสดง LRC breakout pattern
    base_data = []
    
    # สร้างข้อมูล 100 แท่งแรก (trend sideways ใน channel)
    base_price = 45000.0
    for i in range(100):
        # Random walk ภายใน channel
        price_variation = (i % 10 - 5) * 50  # variation ±250
        
        timestamp = 1640995200000 + (i * 3600000)  # 1H intervals
        open_price = base_price + price_variation
        high = open_price + 200
        low = open_price - 200
        close = open_price + ((i % 3) - 1) * 100
        volume = 1000000 + (i % 1000) * 1000
        
        base_data.append([timestamp, open_price, high, low, close, volume])
    
    # เพิ่ม 20 แท่งล่าสุดที่แสดง LRC breakout
    for i in range(100, 120):
        if i >= 117:  # แท่งที่ 3 ล่าสุด - Strong breakout
            timestamp = 1640995200000 + (i * 3600000)
            open_price = 45800 + ((i - 117) * 300)  # Breakout upward
            high = open_price + 400
            low = open_price - 100
            close = open_price + 350  # Strong close near high
            volume = 2500000 + ((i - 117) * 500000)  # Volume spike
        else:
            timestamp = 1640995200000 + (i * 3600000)
            open_price = 45000 + ((i - 100) * 40)
            high = open_price + 150
            low = open_price - 150
            close = open_price + ((i % 2) * 80)
            volume = 1200000
        
        base_data.append([timestamp, open_price, high, low, close, volume])
    
    return base_data

def create_lrc_patterns():
    """สร้าง patterns จำลองสำหรับ Linear Regression Channel"""
    return [
        {
            "type": "Linear Regression Channel",
            "signal": "BREAKOUT_UP",
            "trend_direction": "uptrend",
            "breakout_candles_ago": 2,
            "confidence": 85,
            "pattern_status": "CONFIRMED"
        }
    ]

def test_ai_analyzer():
    """ทดสอบ AI Analyzer พร้อมการปรับปรุง Risk Management"""
    
    print("🧪 ทดสอบ AI Analyzer - Improved Risk Management")
    print("=" * 60)
    
    try:
        # Initialize AI Analyzer
        print("📊 กำลังเริ่มต้น AI Analyzer...")
        ai_analyzer = AIAnalyzer()
        
        # สร้างข้อมูลทดสอบ
        print("📈 กำลังสร้างข้อมูล OHLCV จำลอง...")
        ohlcv_1h = create_sample_ohlcv_data()
        patterns = create_lrc_patterns()
        
        print(f"✅ สร้างข้อมูล {len(ohlcv_1h)} แท่งเทียนสำเร็จ")
        print(f"📊 ราคาปัจจุบัน: {ohlcv_1h[-1][4]:.2f} USDT")
        print(f"🎯 Patterns: {len(patterns)} pattern(s)")
        
        # ทดสอบการวิเคราะห์
        print("\n🤖 กำลังส่งข้อมูลให้ AI วิเคราะห์...")
        print("⚡ ใช้ Linear Regression Channel strategy ใหม่")
        
        result = ai_analyzer.analyze_symbol(
            symbol="BTCUSDT",
            ohlcv_1h=ohlcv_1h,
            previous_patterns=patterns
        )
        
        print("\n📋 ผลการวิเคราะห์จาก AI:")
        print("=" * 50)
        
        # แสดงผลหลัก
        action = result.get('action', 'HOLD')
        confidence = result.get('confidence', 0)
        entry_price = result.get('entry_price', 0)
        stop_loss = result.get('stop_loss', 0)
        take_profit = result.get('take_profit', 0)
        risk_reward_ratio = result.get('risk_reward_ratio', 0)
        
        print(f"🎯 Action: {action}")
        print(f"💯 Confidence: {confidence}%")
        print(f"💰 Entry Price: {entry_price:.2f} USDT")
        print(f"🛑 Stop Loss: {stop_loss:.2f} USDT")
        print(f"🎯 Take Profit: {take_profit:.2f} USDT")
        print(f"📊 Risk-Reward Ratio: {risk_reward_ratio:.2f}:1")
        
        # คำนวณ risk management metrics
        if action != "HOLD" and entry_price > 0:
            if action == "LONG":
                loss_risk = abs(entry_price - stop_loss)
                profit_potential = abs(take_profit - entry_price)
                sl_distance_pct = (loss_risk / entry_price) * 100
                tp_distance_pct = (profit_potential / entry_price) * 100
            else:  # SHORT
                loss_risk = abs(stop_loss - entry_price)
                profit_potential = abs(entry_price - take_profit)
                sl_distance_pct = (loss_risk / entry_price) * 100
                tp_distance_pct = (profit_potential / entry_price) * 100
            
            print(f"\n📊 Risk Management Analysis:")
            print(f"   💸 Loss Risk: {loss_risk:.2f} USDT ({sl_distance_pct:.2f}%)")
            print(f"   💰 Profit Potential: {profit_potential:.2f} USDT ({tp_distance_pct:.2f}%)")
            
            # ตรวจสอบการปรับปรุง
            print(f"\n✅ การปรับปรุง Risk Management:")
            if sl_distance_pct <= 2.0:  # SL ใกล้ Entry
                print(f"   🎯 Stop Loss Conservative: {sl_distance_pct:.2f}% (ดี - ความเสี่ยงต่ำ)")
            else:
                print(f"   ⚠️  Stop Loss: {sl_distance_pct:.2f}% (อาจสูงไป)")
                
            if tp_distance_pct >= 4.0:  # TP ไกล Entry
                print(f"   🚀 Take Profit Aggressive: {tp_distance_pct:.2f}% (ดี - โอกาสกำไรสูง)")
            else:
                print(f"   📉 Take Profit: {tp_distance_pct:.2f}% (อาจใกล้ไป)")
                
            if risk_reward_ratio >= 2.0:
                print(f"   💯 Risk-Reward Ratio: {risk_reward_ratio:.2f}:1 (ดีเยี่ยม)")
            else:
                print(f"   ⚠️  Risk-Reward Ratio: {risk_reward_ratio:.2f}:1 (ควรปรับปรุง)")
        
        # แสดง AI confidence breakdown
        if 'ai_confidence_breakdown' in result:
            breakdown = result['ai_confidence_breakdown']
            print(f"\n🧠 AI Confidence Breakdown:")
            print(f"   🕐 Breakout Freshness: {breakdown.get('breakout_freshness_score', 0)}/10")
            print(f"   📈 Trend Alignment: {breakdown.get('trend_alignment_score', 0)}/10")
            print(f"   🔍 Channel Quality: {breakdown.get('channel_quality_score', 0)}/10")
            print(f"   📊 Volume Confirmation: {breakdown.get('volume_confirmation_score', 0)}/10")
            print(f"   💪 Price Action Strength: {breakdown.get('price_action_strength_score', 0)}/10")
            print(f"   📏 Channel Width Quality: {breakdown.get('channel_width_quality_score', 0)}/10")
        
        print(f"\n📝 Analysis: {result.get('analysis', 'No analysis')}")
        
        # สรุปผล
        print(f"\n{'='*60}")
        if action == "HOLD":
            print("❌ สัญญาณ: HOLD - ไม่เทรด")
            print("🔍 เหตุผล: อาจเป็นเพราะ confidence ต่ำ หรือ risk-reward ไม่เหมาะสม")
        else:
            print(f"✅ สัญญาณ: {action} - พร้อมเทรด")
            print(f"🎯 Confidence: {confidence}%")
            print(f"📊 Risk-Reward: {risk_reward_ratio:.2f}:1")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ai_analyzer()
    if success:
        print("\n✅ การทดสอบเสร็จสิ้น")
    else:
        print("\n❌ การทดสอบล้มเหลว")
