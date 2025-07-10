#!/usr/bin/env python3
"""
Linear Regression Channel Detector - Clean Version
ไม่ใช้ EMA ใช้เงื่อนไขใหม่:
- Long: ราคาอยู่ต่ำกว่าเส้นบนล่าสุด (upper channel)
- Short: ราคาอยู่สูงกว่าเส้นล่างล่าสุด (lower channel)
"""

import json
import sys
import math
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import argparse


@dataclass
class OHLCV:
    """OHLCV data structure"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class LRCResult:
    """Linear Regression Channel analysis result"""
    pattern_type: str  # LRC_BREAKOUT_UP, LRC_BREAKOUT_DOWN, NO_BREAKOUT
    confidence: float
    signal: str  # LONG, SHORT, NEUTRAL
    strength: float  # 1-10 scale
    entry_level: float
    stop_loss: float
    take_profit: float
    volume_confirm: bool
    pattern_status: str  # FRESH_BREAKOUT, OLD_BREAKOUT, NO_BREAKOUT
    description: str
    # LRC specific fields
    upper_channel: float
    middle_line: float
    lower_channel: float
    slope: float
    deviation: float
    trend_direction: str  # UP, DOWN, SIDEWAYS
    breakout_candles_ago: int = 999
    is_fresh_breakout: bool = False


class LinearRegressionChannelDetector:
    """Linear Regression Channel detector with channel price validation"""
    
    def __init__(self, data: List[OHLCV], length: int = 100, deviation: float = 2.0):
        self.data = data
        self.length = length  # Default 100 like TradingView
        self.deviation = deviation  # Default 2.0 like TradingView
        
    def get_channel(self, src_values: List[float], length: int) -> Tuple[float, float, float, float]:
        """
        Calculate Linear Regression Channel components exactly like PineScript
        Returns: (intercept, endy, dev, slope)
        """
        if len(src_values) < length:
            return 0.0, 0.0, 0.0, 0.0
            
        # Take last 'length' values
        src = src_values[-length:]
        
        # Calculate middle line like PineScript: mid = sum(src, len) / len
        mid = sum(src) / length
        
        # Linear regression calculation (matching PineScript linreg function)
        n = length
        sum_x = sum(range(n))  # 0+1+2+...+(n-1)
        sum_x2 = sum(i * i for i in range(n))  # 0^2+1^2+2^2+...+(n-1)^2
        sum_y = sum(src)
        sum_xy = sum(i * src[i] for i in range(n))
        
        # Linear regression slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Calculate intercept exactly like PineScript
        intercept = mid - slope * (length // 2) + ((1 - (length % 2)) / 2) * slope
        
        # Calculate endy (end value of regression line)
        endy = intercept + slope * (length - 1)
        
        # Calculate standard deviation exactly like PineScript
        dev = 0.0
        for x in range(length):
            predicted_value = slope * (length - x) + intercept
            dev += (src[x] - predicted_value) ** 2
        dev = math.sqrt(dev / length)
        
        return intercept, endy, dev, slope
    
    def detect_breakout_with_channel_price_check(self, max_lookback: int = 5) -> LRCResult:
        """
        วิธีใหม่แทน EMA:
        1. ตรวจหา LRC breakout ใน 5 timeframes ย้อนหลัง
        2. ถ้า breakout up → ตรวจว่าราคาปัจจุบันอยู่ต่ำกว่าเส้นบนล่าสุด (upper channel)
        3. ถ้า breakout down → ตรวจว่าราคาปัจจุบันอยู่สูงกว่าเส้นล่างล่าสุด (lower channel)
        4. ถ้าผ่านทุกเงื่อนไข ส่งไป AI
        """
        if len(self.data) < self.length:
            return self._no_signal("insufficient_data")
            
        # ขั้นตอนที่ 1: วน loop 10 รอบ หา LRC breakout
        print(f"        🔄 วน loop {max_lookback} รอบ หา LRC breakout...")
        lrc_breakout_result = self._detect_lrc_breakout_new_method(max_lookback)
        
        if not lrc_breakout_result['has_breakout']:
            return self._no_signal("no_lrc_breakout_found")
        
        # ขั้นตอนที่ 2: ตรวจสอบตำแหน่งราคาปัจจุบันเทียบกับ channel
        breakout_direction = lrc_breakout_result['direction']
        print(f"        ✅ พบ LRC breakout {breakout_direction}!")
        print(f"        🔄 ตรวจสอบตำแหน่งราคาเทียบกับ channel...")
        
        channel_validation_result = self._validate_price_position_vs_channel(breakout_direction)
        
        if not channel_validation_result['is_valid']:
            return self._no_signal(channel_validation_result['reason'])
            
        # ขั้นตอนที่ 3: ผ่านทุกเงื่อนไข - ส่งให้ AI
        print(f"        ✅ ผ่านทุกเงื่อนไข: {breakout_direction} breakout + channel price validation!")
        return self._create_confirmed_signal_from_lrc_with_channel(lrc_breakout_result, channel_validation_result)

    def _detect_lrc_breakout_new_method(self, max_lookback: int) -> Dict[str, Any]:
        """ตรวจหา LRC breakout ย้อนหลัง max_lookback รอบ"""
        for i in range(1, min(max_lookback + 1, len(self.data) - self.length)):
            print(f"        🔍 ตรวจสอบ LRC breakout ที่แท่งเทียน {i} ย้อนหลัง...")
            
            # ใช้ข้อมูลจนถึงจุดที่ i candles ago
            data_until_point = self.data[:-i] if i > 0 else self.data
            
            if len(data_until_point) < self.length:
                continue
            
            # คำนวณ channel ณ จุดนั้น
            closes = [candle.close for candle in data_until_point]
            intercept, endy, dev, slope = self.get_channel(closes, self.length)
            
            if dev == 0:
                continue
            
            # คำนวณ channel lines ณ จุดนั้น
            upper_channel = endy + (self.deviation * dev)
            lower_channel = endy - (self.deviation * dev)
            
            # ตรวจสอบ breakout
            current_candle = data_until_point[-1]
            breakout_result = self._check_breakout_at_point(
                current_candle, upper_channel, lower_channel, endy, i
            )
            
            if breakout_result['has_breakout']:
                print(f"        ✅ พบ LRC breakout {breakout_result['direction']} ที่ {i} candles ago!")
                return {
                    'has_breakout': True,
                    'direction': breakout_result['direction'],
                    'candles_ago': i,
                    'upper_channel': upper_channel,
                    'lower_channel': lower_channel,
                    'middle_line': endy,
                    'slope': slope,
                    'deviation': dev
                }
        
        print(f"        ❌ ไม่พบ LRC breakout ใน {max_lookback} timeframes")
        return {'has_breakout': False}

    def _check_breakout_at_point(self, candle: OHLCV, upper: float, lower: float, middle: float, candles_ago: int) -> Dict[str, Any]:
        """ตรวจสอบ breakout ณ จุดเฉพาะ"""
        # Breakout UP: close หรือ high เหนือ upper channel
        if candle.close > upper or candle.high > upper:
            print(f"            📈 Breakout UP: Close={candle.close:.6f}, High={candle.high:.6f}, Upper={upper:.6f}")
            return {
                'has_breakout': True,
                'direction': 'UP',
                'breakout_price': max(candle.close, candle.high),
                'channel_price': upper
            }
        
        # Breakout DOWN: close หรือ low ต่ำกว่า lower channel
        if candle.close < lower or candle.low < lower:
            print(f"            📉 Breakout DOWN: Close={candle.close:.6f}, Low={candle.low:.6f}, Lower={lower:.6f}")
            return {
                'has_breakout': True,
                'direction': 'DOWN',
                'breakout_price': min(candle.close, candle.low),
                'channel_price': lower
            }
        
        return {'has_breakout': False}

    def _validate_price_position_vs_channel(self, breakout_direction: str) -> Dict[str, Any]:
        """
        ตรวจสอบตำแหน่งราคาปัจจุบันเทียบกับ channel ล่าสุด
        - Long: ราคาอยู่ต่ำกว่าเส้นบนล่าสุด (upper channel)  
        - Short: ราคาอยู่สูงกว่าเส้นล่างล่าสุด (lower channel)
        """
        if len(self.data) < self.length:
            return {'is_valid': False, 'reason': 'insufficient_data_for_channel'}
        
        # คำนวณ channel ล่าสุด
        closes = [candle.close for candle in self.data]
        intercept, endy, dev, slope = self.get_channel(closes, self.length)
        
        if dev == 0:
            return {'is_valid': False, 'reason': 'invalid_channel_calculation'}
        
        # คำนวณ channel lines ล่าสุด
        upper_channel = endy + (self.deviation * dev)
        lower_channel = endy - (self.deviation * dev)
        
        # ราคาปัจจุบัน
        current_price = self.data[-1].close
        
        print(f"        📊 ราคาปัจจุบัน: {current_price:.6f}")
        print(f"        📊 Upper Channel: {upper_channel:.6f}")
        print(f"        📊 Lower Channel: {lower_channel:.6f}")
        
        if breakout_direction == 'UP':
            # Long: ราคาอยู่ต่ำกว่าเส้นบนล่าสุด
            is_valid = current_price < upper_channel
            print(f"        📊 Long Validation: ราคา < Upper? {is_valid}")
            
            if is_valid:
                return {
                    'is_valid': True,
                    'direction': 'LONG',
                    'current_price': current_price,
                    'channel_reference': upper_channel,
                    'validation_type': 'price_below_upper'
                }
            else:
                return {
                    'is_valid': False,
                    'reason': 'price_not_below_upper_channel',
                    'current_price': current_price,
                    'upper_channel': upper_channel
                }
        
        elif breakout_direction == 'DOWN':
            # Short: ราคาอยู่สูงกว่าเส้นล่างล่าสุด
            is_valid = current_price > lower_channel
            print(f"        📊 Short Validation: ราคา > Lower? {is_valid}")
            
            if is_valid:
                return {
                    'is_valid': True,
                    'direction': 'SHORT',
                    'current_price': current_price,
                    'channel_reference': lower_channel,
                    'validation_type': 'price_above_lower'
                }
            else:
                return {
                    'is_valid': False,
                    'reason': 'price_not_above_lower_channel',
                    'current_price': current_price,
                    'lower_channel': lower_channel
                }
        
        return {'is_valid': False, 'reason': 'unknown_breakout_direction'}

    def _create_confirmed_signal_from_lrc_with_channel(self, lrc_result: Dict[str, Any], channel_result: Dict[str, Any]) -> LRCResult:
        """สร้าง LRC signal ที่ผ่าน channel price validation แล้ว"""
        direction = channel_result['direction']
        current_price = channel_result['current_price']
        
        # กำหนด entry, stop loss, take profit
        if direction == 'LONG':
            entry_level = current_price
            # Stop loss = channel reference (upper channel) * 0.98
            stop_loss = channel_result['channel_reference'] * 0.98
            # Take profit = current_price * 1.02
            take_profit = current_price * 1.02
            pattern_type = "LRC_BREAKOUT_UP"
            
        else:  # SHORT
            entry_level = current_price
            # Stop loss = channel reference (lower channel) * 1.02
            stop_loss = channel_result['channel_reference'] * 1.02
            # Take profit = current_price * 0.98
            take_profit = current_price * 0.98
            pattern_type = "LRC_BREAKOUT_DOWN"
        
        return LRCResult(
            pattern_type=pattern_type,
            confidence=85.0,  # High confidence สำหรับ LRC + channel validation
            signal=direction,
            strength=8.0,
            entry_level=entry_level,
            stop_loss=stop_loss,
            take_profit=take_profit,
            volume_confirm=True,
            pattern_status="FRESH_BREAKOUT",
            description=f"lrc_breakout_{direction.lower()}_with_channel_validation",
            upper_channel=lrc_result.get('upper_channel', 0),
            middle_line=lrc_result.get('middle_line', 0),
            lower_channel=lrc_result.get('lower_channel', 0),
            slope=lrc_result.get('slope', 0),
            deviation=lrc_result.get('deviation', 0),
            trend_direction=lrc_result['direction'],
            breakout_candles_ago=lrc_result['candles_ago'],
            is_fresh_breakout=True
        )

    def _no_signal(self, reason: str) -> LRCResult:
        """สร้าง no signal result"""
        return LRCResult(
            pattern_type="NO_BREAKOUT",
            confidence=0.0,
            signal="NEUTRAL",
            strength=0.0,
            entry_level=0.0,
            stop_loss=0.0,
            take_profit=0.0,
            volume_confirm=False,
            pattern_status="NO_BREAKOUT",
            description=reason,
            upper_channel=0.0,
            middle_line=0.0,
            lower_channel=0.0,
            slope=0.0,
            deviation=0.0,
            trend_direction="SIDEWAYS",
            breakout_candles_ago=999,
            is_fresh_breakout=False
        )


def main():
    """Main function for testing"""
    parser = argparse.ArgumentParser(description='Linear Regression Channel Detector - Clean Version')
    parser.add_argument('--test-file', type=str, help='JSON file with OHLCV data for testing')
    args = parser.parse_args()
    
    if args.test_file:
        print(f"🧪 Testing with file: {args.test_file}")
        try:
            with open(args.test_file, 'r') as f:
                test_data = json.load(f)
            
            # Convert to OHLCV objects
            ohlcv_data = []
            for candle in test_data:
                ohlcv_data.append(OHLCV(
                    timestamp=int(candle[0]),
                    open=float(candle[1]),
                    high=float(candle[2]),
                    low=float(candle[3]),
                    close=float(candle[4]),
                    volume=float(candle[5])
                ))
            
            # Test the detector
            detector = LinearRegressionChannelDetector(ohlcv_data)
            result = detector.detect_breakout_with_channel_price_check()
            
            print(f"\n✅ Test Results:")
            print(f"Pattern: {result.pattern_type}")
            print(f"Signal: {result.signal}")
            print(f"Confidence: {result.confidence}%")
            print(f"Entry: {result.entry_level}")
            print(f"Stop Loss: {result.stop_loss}")
            print(f"Take Profit: {result.take_profit}")
            print(f"Description: {result.description}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print("🚀 Linear Regression Channel Detector - Clean Version")
        print("Use --test-file to test with OHLCV data")


if __name__ == "__main__":
    main()
