#!/usr/bin/env python3
"""
Test script for updated LRC + EMA7 validation logic
วิธีใหม่: 
1. Load 120 timeframes
2. วน loop 10 รอบ หา LRC breakout
3. ถ้ามี breakout → ตรวจ EMA7 touch + ราคาปัจจุบัน
4. Stop Loss = EMA7
"""

import sys
import json
from linear_regression_detector import LinearRegressionChannelDetector, OHLCV
import ccxt
import time

def test_new_lrc_ema7_logic():
    """Test the new LRC + EMA7 validation logic"""
    print('📊 Testing New LRC + EMA7 Validation Logic')
    print('=' * 60)
    print('วิธีใหม่:')
    print('1. Load 120 timeframes from Binance')
    print('2. วน loop 10 รอบ หา LRC breakout') 
    print('3. ถ้ามี breakout → ตรวจ EMA7 touch + ราคาปัจจุบัน')
    print('4. Stop Loss = EMA7')
    print('=' * 60)
    
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
                
                # Step 3: Run new LRC + EMA7 validation
                print(f'    🔍 Running LRC + EMA7 validation (10 lookback)...')
                result = lrc_detector.detect_breakout_with_ema7_confirmation(max_lookback=10)
                
                # Step 4: Display results
                print(f'    📊 Result Summary:')
                print(f'        Signal: {result.signal}')
                print(f'        Pattern: {result.pattern_type}')
                print(f'        Confidence: {result.confidence:.1f}%')
                print(f'        Fresh Breakout: {result.is_fresh_breakout}')
                
                if result.is_fresh_breakout and result.signal != 'NEUTRAL':
                    print(f'        ✅ ผ่านเงื่อนไข LRC + EMA7 validation!')
                    print(f'        Breakout: {result.breakout_candles_ago} candles ago')
                    print(f'        Direction: {result.trend_direction}')
                    print(f'        Stop Loss (EMA7): {result.stop_loss:.6f}')
                    print(f'        Take Profit: {result.take_profit:.6f}')
                    print(f'        Entry Level: {result.entry_level:.6f}')
                    print(f'        🚀 Ready to send to AI!')
                else:
                    print(f'        ❌ ไม่ผ่านเงื่อนไข LRC + EMA7 validation')
                    print(f'        Reason: {result.description}')
                    
            except Exception as e:
                print(f'    ❌ Error testing {symbol}: {e}')
                import traceback
                traceback.print_exc()
                
            # Rate limiting
            time.sleep(1)
            
    except Exception as e:
        print(f'❌ General error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_new_lrc_ema7_logic()
