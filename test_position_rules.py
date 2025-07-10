#!/usr/bin/env python3
"""
ทดสอบเงื่อนไขใหม่: trend_direction != 'sideways' และ confidence >= 80%
"""

import json
import os
from linear_regression_detector import LinearRegressionChannelDetector, OHLCV

def test_position_opening_rules():
    """ทดสอบเงื่อนไขการเปิด Position"""
    print("🧪 ทดสอบเงื่อนไขการเปิด Position")
    print("="*60)
    
    # สร้างข้อมูลทดสอบหลายแบบ
    test_cases = [
        {
            'name': 'High Confidence + Uptrend',
            'trend_direction': 'uptrend',
            'confidence': 85,
            'expected': True
        },
        {
            'name': 'High Confidence + Downtrend', 
            'trend_direction': 'downtrend',
            'confidence': 82,
            'expected': True
        },
        {
            'name': 'High Confidence + Sideways',
            'trend_direction': 'sideways',
            'confidence': 90,
            'expected': False  # ไม่ควรเปิด position ใน sideways
        },
        {
            'name': 'Low Confidence + Uptrend',
            'trend_direction': 'uptrend', 
            'confidence': 75,
            'expected': False  # ไม่ควรเปิด position ถ้า confidence < 80%
        },
        {
            'name': 'Low Confidence + Sideways',
            'trend_direction': 'sideways',
            'confidence': 60,
            'expected': False  # ไม่ควรเปิด position ทั้งคู่
        }
    ]
    
    def should_open_position(trend_direction, confidence):
        """ฟังก์ชันตรวจสอบเงื่อนไขการเปิด Position"""
        # เงื่อนไขที่ 1: Trend Direction ไม่เป็น "sideways"
        trend_check = trend_direction.lower() != 'sideways'
        
        # เงื่อนไขที่ 2: Confidence >= 80%
        confidence_check = confidence >= 80
        
        return trend_check and confidence_check
    
    print("🚦 ทดสอบเงื่อนไข:")
    print("-" * 60)
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        trend_direction = case['trend_direction']
        confidence = case['confidence']
        expected = case['expected']
        
        result = should_open_position(trend_direction, confidence)
        
        trend_check = trend_direction.lower() != 'sideways'
        confidence_check = confidence >= 80
        
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        print(f"{i}. {case['name']}")
        print(f"   📈 Trend: {trend_direction} ({'✅' if trend_check else '❌'})")
        print(f"   📊 Confidence: {confidence}% ({'✅' if confidence_check else '❌'})")
        print(f"   🚀 Should Open: {result} (Expected: {expected}) {status}")
        print()
        
        if result != expected:
            all_passed = False
    
    # ทดสอบกับข้อมูลจริง
    print("📊 ทดสอบกับข้อมูลจริง:")
    print("-" * 60)
    
    try:
        # โหลดข้อมูล BTC
        with open('historical_data_cache/BTC_USDT_USDT_1h.json', 'r') as f:
            btc_data = json.load(f)
        
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
        
        # วิเคราะห์ด้วย LRC
        detector = LinearRegressionChannelDetector(ohlcv_data)
        result = detector.detect_breakout_with_channel_price_check()
        
        print(f"🔍 LRC Result:")
        print(f"   Signal: {result.signal}")
        print(f"   Trend Direction: {result.trend_direction}")
        print(f"   Confidence: {result.confidence}%")
        
        # ทดสอบเงื่อนไข
        should_open = should_open_position(result.trend_direction, result.confidence)
        
        trend_check = result.trend_direction.lower() != 'sideways'
        confidence_check = result.confidence >= 80
        
        print(f"   ✅ Trend Check: {trend_check} ({'PASS' if trend_check else 'FAIL - Sideways'})")
        print(f"   ✅ Confidence Check: {confidence_check} ({'PASS' if confidence_check else 'FAIL - Below 80%'})")
        print(f"   🚀 Position Allowed: {should_open}")
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการทดสอบข้อมูลจริง: {e}")
    
    print()
    print("🎯 สรุปผลการทดสอบ:")
    print("=" * 60)
    print(f"{'✅ ผ่านการทดสอบทั้งหมด' if all_passed else '❌ มีการทดสอบที่ไม่ผ่าน'}")
    print(f"✅ เงื่อนไข: trend_direction != 'sideways'")
    print(f"✅ เงื่อนไข: confidence >= 80%")
    print(f"✅ ทั้งสองเงื่อนไขต้องเป็น True")

if __name__ == "__main__":
    test_position_opening_rules()
