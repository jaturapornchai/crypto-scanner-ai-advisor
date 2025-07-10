#!/usr/bin/env python3
"""
ทดสอบการคำนวณ Confidence ของ AI - ตรวจสอบว่า AI คำนวณ confidence จริงหรือไม่
"""

import os
import json
from ai_analyzer import AIAnalyzer
from linear_regression_detector import LinearRegressionChannelDetector, OHLCV

def test_ai_confidence():
    """ทดสอบการคำนวณ Confidence ของ AI"""
    print("🧪 ทดสอบการคำนวณ Confidence ของ AI")
    print("="*60)
    
    # ตรวจสอบ API Key
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("⚠️ ไม่มี DEEPSEEK_API_KEY - ใช้ Mock AI Response")
        test_mock_confidence()
        return
    
    try:
        # โหลดข้อมูลทดสอบ
        with open('historical_data_cache/BTC_USDT_USDT_1h.json', 'r') as f:
            btc_data = json.load(f)
        
        # แปลงเป็น OHLCV objects
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
        
        print(f"📊 โหลดข้อมูล: {len(ohlcv_data)} OHLCV objects")
        
        # ขั้นตอนที่ 1: LRC Detection
        detector = LinearRegressionChannelDetector(ohlcv_data)
        lrc_result = detector.detect_breakout_with_channel_price_check()
        
        print(f"🔍 LRC Result:")
        print(f"   Signal: {lrc_result.signal}")
        print(f"   LRC Confidence: {lrc_result.confidence}% (Placeholder)")
        print(f"   Trend Direction: {lrc_result.trend_direction}")
        print(f"   Breakout Candles Ago: {lrc_result.breakout_candles_ago}")
        print()
        
        # ขั้นตอนที่ 2: AI Analysis
        if lrc_result.signal != "NEUTRAL":
            print("🤖 ขั้นตอนที่ 2: AI Analysis")
            print("-" * 40)
            
            # แปลงข้อมูลเป็น array format สำหรับ AI
            ohlcv_1h = []
            for ohlcv in ohlcv_data:
                ohlcv_1h.append([
                    ohlcv.timestamp,
                    ohlcv.open,
                    ohlcv.high,
                    ohlcv.low,
                    ohlcv.close,
                    ohlcv.volume
                ])
            
            # สร้าง previous_patterns
            current_price = ohlcv_data[-1].close
            previous_patterns = [{
                'type': lrc_result.pattern_type,
                'confidence': lrc_result.confidence,  # 0.0%
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
            
            # เรียก AI Analyzer
            ai_analyzer = AIAnalyzer(None)
            ai_result = ai_analyzer.analyze_symbol('BTC/USDT', ohlcv_1h, None, previous_patterns)
            
            print(f"🎯 AI Result:")
            print(f"   Action: {ai_result.get('action', 'N/A')}")
            print(f"   AI Confidence: {ai_result.get('confidence', 0)}%")
            print(f"   Trend Direction: {ai_result.get('trend_direction', 'N/A')}")
            print(f"   Stop Loss: {ai_result.get('stop_loss', 0)}")
            print(f"   Take Profit: {ai_result.get('take_profit', 0)}")
            print()
            
            # แสดง AI Confidence Breakdown
            breakdown = ai_result.get('ai_confidence_breakdown', {})
            if breakdown:
                print("📊 AI Confidence Breakdown:")
                for key, value in breakdown.items():
                    if 'score' in key:
                        print(f"   {key}: {value}")
                print(f"   {breakdown.get('confidence_calculation', 'N/A')}")
                print()
            
            # ทดสอบเงื่อนไขการเปิด Position
            action = ai_result.get('action', 'HOLD')
            ai_confidence = ai_result.get('confidence', 0)
            ai_trend_direction = ai_result.get('trend_direction', 'unknown')
            
            print("🚦 ทดสอบเงื่อนไขการเปิด Position:")
            print("-" * 40)
            
            trend_check = ai_trend_direction.lower() != 'sideways'
            confidence_check = ai_confidence >= 80
            
            print(f"✅ Action: {action}")
            print(f"✅ Trend Direction: {ai_trend_direction} ({'PASS' if trend_check else 'FAIL - Sideways'})")
            print(f"✅ AI Confidence: {ai_confidence}% ({'PASS' if confidence_check else 'FAIL - Below 80%'})")
            
            position_allowed = (action != 'HOLD') and trend_check and confidence_check
            print(f"🚀 Position Allowed: {'YES' if position_allowed else 'NO'}")
            
            if position_allowed:
                print(f"🎉 ระบบทำงานถูกต้อง - AI คำนวณ confidence {ai_confidence}% และผ่านเงื่อนไข!")
            else:
                print(f"⚠️ Position ไม่ผ่านเงื่อนไข")
                if action == 'HOLD':
                    print(f"   - AI แนะนำ HOLD")
                if not trend_check:
                    print(f"   - Trend Direction เป็น sideways")
                if not confidence_check:
                    print(f"   - AI Confidence ต่ำกว่า 80%")
        else:
            print("⚠️ ไม่พบ LRC breakout - ไม่เรียก AI")
            
    except Exception as e:
        print(f"❌ ข้อผิดพลาด: {e}")

def test_mock_confidence():
    """ทดสอบแบบ Mock เมื่อไม่มี API Key"""
    print("🎭 Mock AI Response Test:")
    print("-" * 30)
    
    # Mock AI responses for testing
    mock_responses = [
        {"action": "LONG", "confidence": 85, "trend_direction": "uptrend"},  # Should PASS
        {"action": "SHORT", "confidence": 82, "trend_direction": "downtrend"},  # Should PASS
        {"action": "LONG", "confidence": 90, "trend_direction": "sideways"},  # Should FAIL (sideways)
        {"action": "LONG", "confidence": 75, "trend_direction": "uptrend"},  # Should FAIL (low confidence)
        {"action": "HOLD", "confidence": 0, "trend_direction": "unknown"},  # Should FAIL (HOLD)
    ]
    
    for i, mock_ai in enumerate(mock_responses, 1):
        action = mock_ai['action']
        confidence = mock_ai['confidence']
        trend_direction = mock_ai['trend_direction']
        
        trend_check = trend_direction.lower() != 'sideways'
        confidence_check = confidence >= 80
        position_allowed = (action != 'HOLD') and trend_check and confidence_check
        
        result = "✅ PASS" if position_allowed else "❌ FAIL"
        
        print(f"{i}. Action:{action}, Confidence:{confidence}%, Trend:{trend_direction} → {result}")

if __name__ == "__main__":
    test_ai_confidence()
