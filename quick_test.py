#!/usr/bin/env python3
"""
Quick test script to verify the Line Breakout + EMA7 system is working correctly
"""

import json
import sys
from exchange_client import ExchangeClient
from ai_analyzer import AIAnalyzer

def test_single_symbol():
    """Test a single symbol to verify the AI analyzer works with new prompt"""
    
    print("🔍 Testing Linear Regression Channel AI analyzer...")
    
    # Initialize components
    exchange = ExchangeClient()
    ai_analyzer = AIAnalyzer()
    
    # Test symbol
    symbol = "BTCUSDT"
    
    print(f"📊 Testing symbol: {symbol}")
    
    # Fetch fresh OHLCV data
    print("📡 Fetching 1H OHLCV data...")
    ohlcv_1h = exchange.get_exchange().fetch_ohlcv(symbol, '1h', limit=20)
    
    if not ohlcv_1h or len(ohlcv_1h) < 20:
        print("❌ Failed to get enough OHLCV data")
        return
    
    print(f"✅ Got {len(ohlcv_1h)} records")
    print(f"� Latest price: {ohlcv_1h[-1][4] if ohlcv_1h else 'N/A'}")
    
    # Create mock pattern data (simulating Python detector output)
    mock_pattern = {
        'pattern': 'LINE_BREAKOUT_UP_EMA7',
        'signal': 'LONG',
        'confidence': 85.0,
        'breakout_candles_ago': 3,
        'ema7_confirmation': 'both'
    }
    
    print("🤖 Testing AI analyzer with mock Linear Regression Channel pattern...")
    
    ai_result = ai_analyzer.analyze_symbol(symbol, ohlcv_1h, None, [mock_pattern])
    
    print(f"🎯 AI analyzer result:")
    print(f"   Action: {ai_result.get('action', 'N/A')}")
    print(f"   Confidence: {ai_result.get('confidence', 0):.1f}%")
    print(f"   Pattern: {ai_result.get('pattern_detected', 'N/A')}")
    print(f"   Entry: {ai_result.get('entry_price', 0)}")
    print(f"   SL: {ai_result.get('stop_loss', 0)}")
    print(f"   TP: {ai_result.get('take_profit', 0)}")
    print(f"   Analysis: {ai_result.get('analysis', 'N/A')}")
    
    # Test with no pattern (should return HOLD)
    print("\n🤖 Testing AI analyzer with no pattern...")
    
    no_pattern_result = ai_analyzer.analyze_symbol(symbol, ohlcv_1h, None, [])
    
    print(f"🎯 No pattern result:")
    print(f"   Action: {no_pattern_result.get('action', 'N/A')}")
    print(f"   Confidence: {no_pattern_result.get('confidence', 0):.1f}%")
    
    print("✅ Test completed")

if __name__ == "__main__":
    test_single_symbol()
