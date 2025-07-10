#!/usr/bin/env python3
"""
Test script for new LRC breakout logic
วิธีใหม่: Load 120 timeframes → วน loop 10 รอบ → ตรวจสอบ LRC breakout → ส่งให้ AI
"""

import sys
import json
from linear_regression_detector import LinearRegressionChannelDetector, OHLCV
import ccxt
import time

def test_new_lrc_logic():
    """Test the new LRC-only breakout detection"""
    print('📊 Testing New LRC Breakout Logic')
    print('=' * 50)
    print('วิธีใหม่: Load 120 timeframes → วน loop 10 รอบ → ตรวจสอบ LRC breakout → ส่งให้ AI')
    print('=' * 50)
    
    try:
        # Create Binance client
        exchange = ccxt.binance()
        
        # Test symbols
        test_symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        
        for symbol in test_symbols:
            print(f'\n🔍 Testing {symbol}...')
            
            try:
                # Step 1: Load 120 timeframes from Binance
                print(f'    📊 Loading 120 timeframes from Binance...')
                ohlcv_data = exchange.fetch_ohlcv(symbol, '1h', limit=120)
                print(f'    ✅ Got {len(ohlcv_data)} timeframes')
                
                # Convert to OHLCV objects
                ohlc_objects = []
                for candle in ohlcv_data:
                    ohlc_obj = OHLCV(
                        timestamp=int(candle[0]),
                        open=float(candle[1]),
                        high=float(candle[2]),
                        low=float(candle[3]),
                        close=float(candle[4]),
                        volume=float(candle[5])
                    )
                    ohlc_objects.append(ohlc_obj)
                
                # Step 2: Create LRC detector and test new method
                print(f'    🔄 Creating LRC detector (length=100, deviation=2.0)...')
                lrc_detector = LinearRegressionChannelDetector(ohlc_objects, length=100, deviation=2.0)
                
                # Step 3: Run new LRC breakout detection (10 lookback)
                print(f'    🔍 Running new LRC breakout detection (10 lookback)...')
                result = lrc_detector.detect_breakout_with_ema7_confirmation(max_lookback=10)
                
                # Step 4: Display results
                print(f'    📊 Result Summary:')
                print(f'        Signal: {result.signal}')
                print(f'        Pattern: {result.pattern_type}')
                print(f'        Confidence: {result.confidence:.1f}%')
                print(f'        Fresh Breakout: {result.is_fresh_breakout}')
                
                if result.is_fresh_breakout:
                    print(f'        ✅ Breakout found {result.breakout_candles_ago} candles ago')
                    print(f'        Trend Direction: {result.trend_direction}')
                    print(f'        Slope: {result.slope:.6f}')
                    print(f'        Upper Channel: {result.upper_channel:.6f}')
                    print(f'        Lower Channel: {result.lower_channel:.6f}')
                    print(f'        🚀 Ready to send to AI!')
                else:
                    print(f'        ❌ No breakout found in 10 timeframes')
                    
            except Exception as e:
                print(f'    ❌ Error testing {symbol}: {e}')
                
            # Rate limiting
            time.sleep(1)
            
    except Exception as e:
        print(f'❌ General error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_new_lrc_logic()
