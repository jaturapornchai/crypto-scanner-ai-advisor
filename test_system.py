#!/usr/bin/env python3
"""
Test Script for Linear Regression Channel Trading System
ทดสอบระบบเทรด Linear Regression Channel
"""

import sys
import json
import time
from datetime import datetime

def test_imports():
    """ทดสอบการ import modules ที่จำเป็น"""
    print("🧪 ทดสอบการ import modules...")
    
    try:
        import ccxt
        print(f"✅ CCXT: {ccxt.__version__}")
    except ImportError as e:
        print(f"❌ CCXT: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy: {e}")
        return False
    
    try:
        import pandas as pd
        print(f"✅ Pandas: {pd.__version__}")
    except ImportError as e:
        print(f"❌ Pandas: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv: OK")
    except ImportError as e:
        print(f"❌ Python-dotenv: {e}")
        return False
    
    return True

def test_exchange_connection():
    """ทดสอบการเชื่อมต่อ Exchange"""
    print("\n🧪 ทดสอบการเชื่อมต่อ Binance Futures...")
    
    try:
        from exchange_client import ExchangeClient
        
        client = ExchangeClient()
        if client.test_connection():
            print("✅ เชื่อมต่อ Binance สำเร็จ!")
            
            # ทดสอบดึงข้อมูล symbols
            exchange = client.get_exchange()
            symbols = [s for s in exchange.symbols if 'USDT' in s and '/USDT:USDT' in s]
            print(f"📊 พบ USDT Futures: {len(symbols)} symbols")
            print(f"📊 ตัวอย่าง: {symbols[:3]}")
            return True
        else:
            print("❌ เชื่อมต่อ Binance ล้มเหลว!")
            return False
    except Exception as e:
        print(f"❌ ข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return False

def test_lrc_detector():
    """ทดสอบ Linear Regression Channel Detector"""
    print("\n🧪 ทดสอบ Linear Regression Channel Detector...")
    
    try:
        from linear_regression_channel import LinearRegressionChannelDetector
        
        # สร้างข้อมูลทดสอบ
        test_data = []
        base_price = 45000
        for i in range(150):  # ข้อมูล 150 แท่งเทียน
            price = base_price + (i * 10) + (20 * (i % 10 - 5))  # แนวโน้มขึ้นพร้อม noise
            test_data.append({
                'timestamp': int(time.time()) - (150 - i) * 3600,
                'open': price - 5,
                'high': price + 15,
                'low': price - 10,
                'close': price,
                'volume': 100 + (i % 50)
            })
        
        # ทดสอบ LRC detector
        detector = LinearRegressionChannelDetector(length=100, deviation=2.0, lookback_candles=5)
        
        # คำนวณ channel
        channel_data = detector.calculate_linear_regression_channel(test_data)
        if channel_data:
            print("✅ คำนวณ Linear Regression Channel สำเร็จ!")
            print(f"📊 Upper Channel: {channel_data['upper_line']:.2f}")
            print(f"📊 Middle Line: {channel_data['middle_line']:.2f}")
            print(f"📊 Lower Channel: {channel_data['lower_line']:.2f}")
            print(f"📊 Slope: {channel_data['slope']:.6f}")
            
            # ทดสอบการตรวจจับ breakout
            breakout_data = detector.detect_fresh_breakout(test_data, channel_data)
            if breakout_data:
                print("✅ ตรวจจับ breakout สำเร็จ!")
                print(f"📊 Breakout Type: {breakout_data['breakout_type']}")
                print(f"📊 Candles Ago: {breakout_data['candles_ago']}")
                print(f"📊 Volume Confirmed: {breakout_data['volume_confirmed']}")
            else:
                print("📊 ไม่พบ fresh breakout ในข้อมูลทดสอบ")
            
            return True
        else:
            print("❌ ไม่สามารถคำนวณ Linear Regression Channel ได้")
            return False
            
    except Exception as e:
        print(f"❌ ข้อผิดพลาดใน LRC Detector: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pattern_detector():
    """ทดสอบ Pattern Detector (LRC only)"""
    print("\n🧪 ทดสอบ Pattern Detector...")
    
    try:
        from pattern_detector import analyze_lrc_breakout
        
        # สร้างข้อมูลทดสอบ
        test_ohlcv = []
        base_price = 45000
        for i in range(120):
            price = base_price + (i * 5)  # แนวโน้มขึ้น
            test_ohlcv.append([
                int(time.time()) - (120 - i) * 3600000,  # timestamp
                price - 2,  # open
                price + 10,  # high
                price - 5,  # low
                price,  # close
                100 + i  # volume
            ])
        
        # วิเคราะห์ LRC breakout
        result = analyze_lrc_breakout("BTCUSDT", test_ohlcv, debug=True)
        
        print("✅ Pattern Detector ทำงานสำเร็จ!")
        print(f"📊 Symbol: {result.get('symbol', 'N/A')}")
        print(f"📊 Has Fresh Breakout: {result.get('has_fresh_breakout', False)}")
        print(f"📊 Breakout Type: {result.get('breakout_type', 'None')}")
        print(f"📊 Confidence: {result.get('confidence', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ข้อผิดพลาดใน Pattern Detector: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_integration():
    """ทดสอบการ integrate กับ AI"""
    print("\n🧪 ทดสอบ AI Integration...")
    
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        if deepseek_key:
            print("✅ DeepSeek API Key พบแล้ว")
            
            # ทดสอบ import ai_analyzer
            try:
                from ai_analyzer import AIAnalyzer
                analyzer = AIAnalyzer()
                print("✅ AI Analyzer สร้างสำเร็จ!")
                return True
            except Exception as e:
                print(f"⚠️  AI Analyzer: {e}")
                return False
        else:
            print("⚠️  ไม่พบ DeepSeek API Key")
            return False
            
    except Exception as e:
        print(f"❌ ข้อผิดพลาดใน AI Integration: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 เริ่มทดสอบระบบ Linear Regression Channel Trading")
    print("=" * 60)
    print("⚠️  ระบบนี้ใช้เงินจริงในการเทรด - กรุณาใช้ระบบทดสอบก่อน!")
    print("=" * 60)
    
    tests = [
        ("Import Modules", test_imports),
        ("Exchange Connection", test_exchange_connection),
        ("LRC Detector", test_lrc_detector),
        ("Pattern Detector", test_pattern_detector),
        ("AI Integration", test_ai_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print("="*60)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # สรุปผลการทดสอบ
    print(f"\n{'='*60}")
    print("📋 สรุปผลการทดสอบ")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 ผลการทดสอบ: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ระบบพร้อมใช้งาน!")
        print("🚀 รันคำสั่ง: python app.py")
    else:
        print("⚠️  มีปัญหาที่ต้องแก้ไขก่อนใช้งาน")
        print("🔧 กรุณาตรวจสอบการติดตั้งและการตั้งค่า")

if __name__ == "__main__":
    main()
