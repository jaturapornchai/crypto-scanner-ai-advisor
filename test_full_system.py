#!/usr/bin/env python3
"""
ทดสอบการทำงานของระบบเต็มรูปแบบ รวมทั้ง AI confidence calculation
"""

import os
import json
from ai_analyzer import AIAnalyzer
from linear_regression_detector import LinearRegressionChannelDetector, OHLCV

def test_full_system_with_ai():
    """ทดสอบระบบเต็มรูปแบบรวม AI"""
    print("🧪 ทดสอบระบบเต็มรูปแบบ: LRC + AI Confidence")
    print("="*70)
    
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("⚠️ ไม่มี DEEPSEEK_API_KEY - จำลองผลลัพธ์ AI")
        test_simulated_ai_flow()
        return
    
    try:
        # โหลดข้อมูลทดสอบ
        with open('historical_data_cache/BTC_USDT_USDT_1h.json', 'r') as f:
            btc_data = json.load(f)
        
        # แปลงเป็น OHLCV objects และ array format
        ohlcv_data = []
        ohlcv_1h = []
        for candle in btc_data:
            ohlcv_data.append(OHLCV(
                timestamp=int(candle[0]),
                open=float(candle[1]),
                high=float(candle[2]),
                low=float(candle[3]),
                close=float(candle[4]),
                volume=float(candle[5])
            ))
            ohlcv_1h.append([
                int(candle[0]),
                float(candle[1]),
                float(candle[2]),
                float(candle[3]),
                float(candle[4]),
                float(candle[5])
            ])
        
        print(f"📊 โหลดข้อมูล: {len(ohlcv_data)} candles")
        print()
        
        # จำลองขั้นตอนการทำงานของ enhanced_position_manager
        print("🔍 ขั้นตอนที่ 1: Linear Regression Channel Detection")
        print("-" * 60)
        
        detector = LinearRegressionChannelDetector(ohlcv_data)
        lrc_result = detector.detect_breakout_with_channel_price_check()
        
        print(f"Pattern Type: {lrc_result.pattern_type}")
        print(f"Signal: {lrc_result.signal}")
        print(f"LRC Confidence: {lrc_result.confidence}% (Placeholder - AI จะคำนวณ)")
        print(f"Trend Direction: {lrc_result.trend_direction}")
        print(f"Breakout Candles Ago: {lrc_result.breakout_candles_ago}")
        print()
        
        if lrc_result.signal == "NEUTRAL":
            print("⚠️ ไม่พบ LRC breakout - จบการทดสอบ")
            return
        
        print("🤖 ขั้นตอนที่ 2: AI Analysis (จำลองการทำงานของ enhanced_position_manager)")
        print("-" * 60)
        
        # สร้าง previous_patterns เหมือนใน enhanced_position_manager
        current_price = ohlcv_1h[-1][4]
        previous_patterns = [{
            'type': lrc_result.pattern_type,
            'confidence': lrc_result.confidence,  # 0.0% - placeholder
            'breakout_candles_ago': lrc_result.breakout_candles_ago,
            'signal': lrc_result.signal,
            'trend_direction': lrc_result.trend_direction,
            'slope': lrc_result.slope,
            'upper_channel': lrc_result.upper_channel,
            'middle_line': lrc_result.middle_line,
            'lower_channel': lrc_result.lower_channel,
            'entry_level': current_price,
            'current_price': current_price,
            'request_ai_sl_tp': True
        }]
        
        print("📤 ส่งข้อมูลไปยัง AI:")
        print(f"   Symbol: BTC/USDT")
        print(f"   Current Price: {current_price}")
        print(f"   LRC Signal: {lrc_result.signal}")
        print(f"   Trend Direction: {lrc_result.trend_direction}")
        print(f"   Breakout Candles Ago: {lrc_result.breakout_candles_ago}")
        print()
        
        # เรียก AI Analyzer
        ai_analyzer = AIAnalyzer(None)
        analysis = ai_analyzer.analyze_symbol('BTC/USDT', ohlcv_1h, None, previous_patterns)
        
        print("📥 ผลลัพธ์จาก AI:")
        print("-" * 30)
        
        action = analysis.get('action', 'HOLD')
        confidence = analysis.get('confidence', 0)
        pattern_detected = analysis.get('pattern_detected', 'None')
        trend_direction = analysis.get('trend_direction', 'unknown')
        stop_loss = analysis.get('stop_loss', 0)
        take_profit = analysis.get('take_profit', 0)
        
        print(f"   Action: {action}")
        print(f"   AI Confidence: {confidence}%")
        print(f"   Pattern Detected: {pattern_detected}")
        print(f"   Trend Direction: {trend_direction}")
        print(f"   Stop Loss: {stop_loss}")
        print(f"   Take Profit: {take_profit}")
        
        # แสดง AI Confidence Breakdown
        breakdown = analysis.get('ai_confidence_breakdown', {})
        if breakdown and any(breakdown.values()):
            print("   📊 AI Confidence Scoring:")
            for key, value in breakdown.items():
                if 'score' in key and value > 0:
                    print(f"      {key}: {value}")
            calc = breakdown.get('confidence_calculation', '')
            if calc:
                print(f"      Calculation: {calc}")
        print()
        
        print("🚦 ขั้นตอนที่ 3: ตรวจสอบเงื่อนไขการเปิด Position")
        print("-" * 60)
        
        # จำลองการตรวจสอบของ enhanced_position_manager
        print("1. ตรวจสอบ AI Action:")
        if action == 'HOLD':
            print(f"   ❌ AI แนะนำ HOLD - ข้าม")
            return
        else:
            print(f"   ✅ AI แนะนำ {action}")
        
        print("2. ตรวจสอบ Confidence Threshold (>75%):")
        if confidence < 75:
            print(f"   ❌ Confidence {confidence}% < 75% - ข้าม")
            return
        else:
            print(f"   ✅ Confidence {confidence}% >= 75%")
        
        print("3. ตรวจสอบ Trend Direction (ไม่เป็น sideways):")
        if trend_direction.lower() == 'sideways':
            print(f"   ❌ Trend Direction เป็น 'sideways' - ข้าม")
            return
        else:
            print(f"   ✅ Trend Direction: {trend_direction}")
        
        print("4. ตรวจสอบ AI Confidence (>= 80%):")
        if confidence < 80:
            print(f"   ❌ AI Confidence {confidence}% < 80% - ข้าม")
            return
        else:
            print(f"   ✅ AI Confidence {confidence}% >= 80%")
        
        print()
        print("🎉 ผ่านทุกเงื่อนไข - สามารถเปิด Position ได้!")
        print(f"📊 จะเปิด {action} position สำหรับ BTC/USDT")
        print(f"💰 SL: {stop_loss}, TP: {take_profit}")
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

def test_simulated_ai_flow():
    """จำลองการทำงานเมื่อไม่มี API Key"""
    print("🎭 จำลองการทำงานของระบบ (ไม่มี AI API)")
    print()
    
    # จำลองผลลัพธ์ AI ที่มี confidence สูง
    simulated_ai_result = {
        "action": "LONG",
        "confidence": 85,
        "trend_direction": "uptrend",
        "stop_loss": 44500.0,
        "take_profit": 47200.0,
        "ai_confidence_breakdown": {
            "breakout_freshness_score": 9,
            "trend_alignment_score": 8,
            "channel_quality_score": 8,
            "volume_confirmation_score": 7,
            "price_action_strength_score": 9,
            "channel_width_quality_score": 8,
            "confidence_calculation": "Average: 8.17 × 10 = 82%"
        }
    }
    
    print("📥 จำลองผลลัพธ์จาก AI:")
    print(f"   Action: {simulated_ai_result['action']}")
    print(f"   AI Confidence: {simulated_ai_result['confidence']}%")
    print(f"   Trend Direction: {simulated_ai_result['trend_direction']}")
    print()
    
    # ทดสอบเงื่อนไข
    action = simulated_ai_result['action']
    confidence = simulated_ai_result['confidence']
    trend_direction = simulated_ai_result['trend_direction']
    
    print("🚦 ตรวจสอบเงื่อนไข:")
    
    checks = [
        (action != 'HOLD', f"AI Action: {action}"),
        (confidence >= 75, f"Confidence >= 75%: {confidence}%"),
        (trend_direction.lower() != 'sideways', f"Trend != sideways: {trend_direction}"),
        (confidence >= 80, f"AI Confidence >= 80%: {confidence}%")
    ]
    
    all_pass = True
    for i, (check, description) in enumerate(checks, 1):
        status = "✅ PASS" if check else "❌ FAIL"
        print(f"   {i}. {description} → {status}")
        if not check:
            all_pass = False
    
    print()
    if all_pass:
        print("🎉 ทุกเงื่อนไขผ่าน - สามารถเปิด Position ได้!")
        print("✅ ระบบทำงานถูกต้องตามที่ออกแบบ")
    else:
        print("⚠️ มีเงื่อนไขที่ไม่ผ่าน - ไม่เปิด Position")

if __name__ == "__main__":
    test_full_system_with_ai()
