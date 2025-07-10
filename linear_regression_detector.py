#!/usr/bin/env python3
"""
Linear Regression Channel Detector - Python Implementation
Based on TradingView Linear Regression Channel script by LonesomeTheBlue.
Detects channel breakouts for trading signals.
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
    """Linear Regression Channel detector based on TradingView script"""
    
    def __init__(self, data: List[OHLCV], length: int = 100, deviation: float = 2.0):
        self.data = data
        self.length = length  # Default 100 like TradingView
        self.deviation = deviation  # Default 2.0 like TradingView
        self.ema7_period = 7  # EMA7 period for confirmation
        
    def get_channel(self, src_values: List[float], length: int) -> Tuple[float, float, float, float]:
        """
        Calculate Linear Regression Channel components exactly like PineScript
        Returns: (intercept, endy, dev, slope)
        Based on PineScript get_channel() function
        """
        if len(src_values) < length:
            return 0.0, 0.0, 0.0, 0.0
            
        # Take last 'length' values
        src = src_values[-length:]
        
        # Calculate middle line like PineScript: mid = sum(src, len) / len
        mid = sum(src) / length
        
        # Calculate slope exactly like PineScript: linreg(src, len, 0) - linreg(src, len, 1)
        # This represents the slope between current bar and previous bar of linear regression
        
        # Linear regression calculation (matching PineScript linreg function)
        n = length
        sum_x = sum(range(n))  # 0+1+2+...+(n-1)
        sum_x2 = sum(i * i for i in range(n))  # 0^2+1^2+2^2+...+(n-1)^2
        sum_y = sum(src)
        sum_xy = sum(i * src[i] for i in range(n))
        
        # Linear regression slope
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Calculate intercept exactly like PineScript
        # intercept = mid - slope * floor(len / 2) + ((1 - (len % 2)) / 2) * slope
        intercept = mid - slope * (length // 2) + ((1 - (length % 2)) / 2) * slope
        
        # Calculate endy (end value of regression line)
        # endy = intercept + slope * (len - 1)
        endy = intercept + slope * (length - 1)
        
        # Calculate standard deviation exactly like PineScript
        # for x = 0 to len - 1: dev := dev + pow(src[x] - (slope * (len - x) + intercept), 2)
        # dev := sqrt(dev/len)
        dev = 0.0
        for x in range(length):
            predicted_value = slope * (length - x) + intercept
            dev += (src[x] - predicted_value) ** 2
        dev = math.sqrt(dev / length)
        
        return intercept, endy, dev, slope
    
    def detect_breakout_with_ema7_confirmation(self, max_lookback: int = 10) -> LRCResult:
        """
        วิธีใหม่ตามที่ต้องการ:
        1. Load 120 timeframes จาก Binance (ทำใน enhanced_position_manager.py แล้ว)
        2. วน loop 10 รอบ จากชั่วโมงก่อนหน้า แล้วส่งให้ Linear Regression Channel ดูว่า breakout หรือไม่
        3. ถ้า breakout up → ตรวจ 3 แท่งล่าสุดทับ EMA7 → ราคาล่าสุด > EMA7
        4. ถ้า breakout down → ตรวจ 3 แท่งล่าสุดทับ EMA7 → ราคาล่าสุด < EMA7  
        5. ถ้าผ่านทุกเงื่อนไข ส่งไป AI
        """
        if len(self.data) < self.length:
            return self._no_signal("insufficient_data")
            
        # ขั้นตอนที่ 1: วน loop 10 รอบ หา LRC breakout
        print(f"        🔄 วน loop {max_lookback} รอบ หา LRC breakout...")
        lrc_breakout_result = self._detect_lrc_breakout_new_method(max_lookback)
        
        if not lrc_breakout_result['has_breakout']:
            return self._no_signal("no_lrc_breakout_found")
        
        # ขั้นตอนที่ 2: ตรวจสอบ EMA7 และราคาปัจจุบันตามทิศทาง breakout
        breakout_direction = lrc_breakout_result['direction']
        print(f"        ✅ พบ LRC breakout {breakout_direction}!")
        print(f"        🔄 ตรวจสอบ EMA7 touch และราคาปัจจุบัน...")
        
        ema7_validation_result = self._validate_ema7_for_breakout_direction(breakout_direction)
        
        if not ema7_validation_result['is_valid']:
            return self._no_signal(ema7_validation_result['reason'])
            
        # ขั้นตอนที่ 3: ผ่านทุกเงื่อนไข - ส่งให้ AI
        print(f"        ✅ ผ่านทุกเงื่อนไข: {breakout_direction} breakout + EMA7 validation!")
        return self._create_confirmed_signal_from_lrc_with_ema7(lrc_breakout_result, ema7_validation_result)
    
    def _detect_ema7_cross_in_last_2_timeframes(self) -> Dict[str, Any]:
        """
        วิธีใหม่: ตรวจสอบ EMA7 cross เฉพาะใน 2 timeframes ล่าสุดเท่านั้น
        1. ตรวจสอบแท่งเทียนล่าสุด (candles_ago = 1)
        2. ตรวจสอบแท่งเทียนก่อนหน้า (candles_ago = 2)
        3. ถ้าเจอ cross ก็จบทันที
        """
        if len(self.data) < self.ema7_period + 2:
            return {'has_cross': False, 'reason': 'insufficient_data', 'candles_ago': 0}
        
        # คำนวณ EMA7 สำหรับข้อมูลทั้งหมด
        ema_values = self.calculate_ema7()
        if len(ema_values) < 2:
            return {'has_cross': False, 'reason': 'insufficient_ema_data', 'candles_ago': 0}
        
        # ตรวจสอบเฉพาะ 2 timeframes ล่าสุด
        for i in range(1, 3):  # i = 1, 2 (เฉพาะ 2 timeframes)
            print(f"        🔍 ตรวจสอบ EMA7 cross ที่แท่งเทียน {i} ย้อนหลัง...")
            
            # ดึงข้อมูล 2 แท่งเทียนล่าสุด ณ จุดนั้น
            candle1_index = len(self.data) - i  # แท่งเทียนล่าสุด ณ จุดนั้น
            candle2_index = len(self.data) - i - 1  # แท่งเทียนก่อนหน้า ณ จุดนั้น
            
            if candle2_index < 0 or candle1_index >= len(self.data):
                continue
                
            candle1 = self.data[candle1_index]
            candle2 = self.data[candle2_index]
            ema7_1 = ema_values[candle1_index]
            ema7_2 = ema_values[candle2_index]
            
            # ตรวจสอบว่าแท่งเทียนทับ EMA7 หรือไม่
            candle1_crosses = (
                (candle1.low <= ema7_1 <= candle1.high) or  # EMA7 อยู่ในช่วง high-low
                (min(candle1.open, candle1.close) <= ema7_1 <= max(candle1.open, candle1.close))  # EMA7 อยู่ในตัวเทียน
            )
            
            candle2_crosses = (
                (candle2.low <= ema7_2 <= candle2.high) or  # EMA7 อยู่ในช่วง high-low
                (min(candle2.open, candle2.close) <= ema7_2 <= max(candle2.open, candle2.close))  # EMA7 อยู่ในตัวเทียน
            )
            
            # ต้องมีอย่างน้อย 1 แท่งเทียนที่ทับ EMA7
            has_cross = candle1_crosses or candle2_crosses
            
            if has_cross:
                cross_description = ""
                if candle1_crosses and candle2_crosses:
                    cross_description = "both_candles_cross_ema7"
                elif candle1_crosses:
                    cross_description = "latest_candle_cross_ema7"
                elif candle2_crosses:
                    cross_description = "previous_candle_cross_ema7"
                
                print(f"        ✅ พบ EMA7 cross ที่แท่งเทียน {i} ย้อนหลัง! ({cross_description})")
                print(f"        📊 EMA7: {ema7_1:.6f}, Candle1: O:{candle1.open:.6f} H:{candle1.high:.6f} L:{candle1.low:.6f} C:{candle1.close:.6f}")
                
                return {
                    'has_cross': True,
                    'candles_ago': i,
                    'description': cross_description,
                    'candle1_crosses': candle1_crosses,
                    'candle2_crosses': candle2_crosses,
                    'ema7_latest': ema7_1,
                    'ema7_previous': ema7_2
                }
            else:
                print(f"        ❌ ไม่พบ EMA7 cross ที่แท่งเทียน {i} ย้อนหลัง")
                print(f"        📊 EMA7: {ema7_1:.6f}, Candle: O:{candle1.open:.6f} H:{candle1.high:.6f} L:{candle1.low:.6f} C:{candle1.close:.6f}")
        
        # ไม่พบ EMA7 cross ใน 2 timeframes
        print(f"        ❌ ไม่พบ EMA7 cross ใน 2 timeframes ล่าสุด")
        return {
            'has_cross': False,
            'candles_ago': 0,
            'description': "no_ema7_cross_in_last_2_timeframes",
            'reason': 'no_cross_found_in_2_timeframes'
        }

    def _detect_ema7_cross_in_lookback(self, max_lookback: int = 10) -> Dict[str, Any]:
        """
        วิธีใหม่: ตรวจสอบ EMA7 cross ย้อนหลัง 10 timeframes
        1. วน loop 10 รอบ จากชั่วโมงก่อนหน้า  
        2. ตรวจสอบว่าในแต่ละจุด มี EMA7 cross ใน 2 แท่งเทียนล่าสุด (ณ จุดนั้น) หรือไม่
        3. ถ้าเจอ cross ก็จบ loop ทันที
        """
        if len(self.data) < self.ema7_period + max_lookback + 2:
            return {'has_cross': False, 'reason': 'insufficient_data', 'candles_ago': 0}
        
        # คำนวณ EMA7 สำหรับข้อมูลทั้งหมด
        ema_values = self.calculate_ema7()
        if len(ema_values) < max_lookback + 2:
            return {'has_cross': False, 'reason': 'insufficient_ema_data', 'candles_ago': 0}
        
        # วน loop 10 รอบ จากชั่วโมงก่อนหน้า
        for i in range(1, min(max_lookback + 1, len(self.data) - 1)):
            print(f"        🔍 ตรวจสอบ EMA7 cross ที่แท่งเทียน {i} ย้อนหลัง...")
            
            # ดึงข้อมูล 2 แท่งเทียนล่าสุด ณ จุดนั้น
            candle1_index = len(self.data) - i  # แท่งเทียนล่าสุด ณ จุดนั้น
            candle2_index = len(self.data) - i - 1  # แท่งเทียนก่อนหน้า ณ จุดนั้น
            
            if candle2_index < 0 or candle1_index >= len(self.data):
                continue
                
            candle1 = self.data[candle1_index]
            candle2 = self.data[candle2_index]
            ema7_1 = ema_values[candle1_index]
            ema7_2 = ema_values[candle2_index]
            
            # ตรวจสอบว่าแท่งเทียนทับ EMA7 หรือไม่
            candle1_crosses = (
                (candle1.low <= ema7_1 <= candle1.high) or  # EMA7 อยู่ในช่วง high-low
                (min(candle1.open, candle1.close) <= ema7_1 <= max(candle1.open, candle1.close))  # EMA7 อยู่ในตัวเทียน
            )
            
            candle2_crosses = (
                (candle2.low <= ema7_2 <= candle2.high) or  # EMA7 อยู่ในช่วง high-low
                (min(candle2.open, candle2.close) <= ema7_2 <= max(candle2.open, candle2.close))  # EMA7 อยู่ในตัวเทียน
            )
            
            # ต้องมีอย่างน้อย 1 แท่งเทียนที่ทับ EMA7
            has_cross = candle1_crosses or candle2_crosses
            
            if has_cross:
                cross_description = ""
                if candle1_crosses and candle2_crosses:
                    cross_description = "both_candles_cross_ema7"
                elif candle1_crosses:
                    cross_description = "latest_candle_cross_ema7"
                elif candle2_crosses:
                    cross_description = "previous_candle_cross_ema7"
                
                print(f"        ✅ พบ EMA7 cross ที่แท่งเทียน {i} ย้อนหลัง! ({cross_description})")
                print(f"        📊 EMA7: {ema7_1:.6f}, Candle1: O:{candle1.open:.6f} H:{candle1.high:.6f} L:{candle1.low:.6f} C:{candle1.close:.6f}")
                
                return {
                    'has_cross': True,
                    'candles_ago': i,
                    'description': cross_description,
                    'candle1_crosses': candle1_crosses,
                    'candle2_crosses': candle2_crosses,
                    'ema7_latest': ema7_1,
                    'ema7_previous': ema7_2
                }
            else:
                print(f"        ❌ ไม่พบ EMA7 cross ที่แท่งเทียน {i} ย้อนหลัง")
                print(f"        📊 EMA7: {ema7_1:.6f}, Candle: O:{candle1.open:.6f} H:{candle1.high:.6f} L:{candle1.low:.6f} C:{candle1.close:.6f}")
        
        # ไม่พบ EMA7 cross ในทุกรอบ
        print(f"        ❌ ไม่พบ EMA7 cross ในทั้ง {max_lookback} แท่งเทียนย้อนหลัง")
        return {
            'has_cross': False,
            'candles_ago': 0,
            'description': "no_ema7_cross_found",
            'reason': 'no_cross_found'
        }

    def _detect_lrc_breakout_at_specific_point(self, candles_ago: int) -> Dict[str, Any]:
        """
        ตรวจสอบ LRC breakout ณ จุดเฉพาะที่ระบุ (ที่พบ EMA25 cross)
        """
        if candles_ago <= 0 or candles_ago >= len(self.data):
            return {'has_breakout': False, 'reason': 'invalid_candles_ago'}
            
        print(f"        🔍 ตรวจสอบ LRC breakout ที่แท่งเทียน {candles_ago} ย้อนหลัง...")
        
        # สร้าง dataset สำหรับแท่งเทียนที่ candles_ago ย้อนหลัง
        # ใช้ข้อมูล length แท่งเทียน ณ จุดนั้น
        end_index = len(self.data) - candles_ago
        start_index = max(0, end_index - self.length)
        
        if end_index - start_index < self.length:
            return {'has_breakout': False, 'reason': 'insufficient_data_at_point'}
        
        # ดึงข้อมูลสำหรับการคำนวณ LRC ณ จุดนั้น
        historical_data = self.data[start_index:end_index]
        close_prices = [candle.close for candle in historical_data]
        
        # คำนวณ Linear Regression Channel สำหรับจุดนั้น
        intercept, endy, dev, slope = self.get_channel(close_prices, len(close_prices))
        
        if dev == 0:
            return {'has_breakout': False, 'reason': 'zero_deviation'}
        
        # คำนวณ channel lines ณ จุดนั้น
        y2_ = endy
        upper_channel = y2_ + dev * self.deviation
        lower_channel = y2_ - dev * self.deviation
        
        # ราคา close ณ จุดนั้น
        current_close = historical_data[-1].close
        
        # ตรวจสอบ breakout ตาม PineScript logic
        breakout_found = False
        breakout_direction = ""
        
        if slope > 0 and current_close < lower_channel:
            # Downward breakout in uptrend
            breakout_found = True
            breakout_direction = "DOWN"
            print(f"        ✅ พบ DOWN breakout ที่แท่งเทียน {candles_ago} ย้อนหลัง!")
            print(f"        📊 Close: {current_close:.6f} < Lower: {lower_channel:.6f} (Slope: {slope:.6f})")
        elif slope < 0 and current_close > upper_channel:
            # Upward breakout in downtrend  
            breakout_found = True
            breakout_direction = "UP"
            print(f"        ✅ พบ UP breakout ที่แท่งเทียน {candles_ago} ย้อนหลัง!")
            print(f"        📊 Close: {current_close:.6f} > Upper: {upper_channel:.6f} (Slope: {slope:.6f})")
        else:
            print(f"        ❌ ไม่พบ breakout ที่แท่งเทียน {candles_ago} ย้อนหลัง")
            print(f"        📊 Close: {current_close:.6f}, Upper: {upper_channel:.6f}, Lower: {lower_channel:.6f}")
        
        return {
            'has_breakout': breakout_found,
            'direction': breakout_direction,
            'candles_ago': candles_ago,
            'slope': slope,
            'upper_channel': upper_channel,
            'middle_line': y2_,
            'lower_channel': lower_channel,
            'deviation': dev,
            'trend_direction': "UP" if slope > 0 else "DOWN" if slope < 0 else "SIDEWAYS",
            'close_price': current_close
        }

    def _detect_lrc_breakout_new_method(self, max_lookback: int = 10) -> Dict[str, Any]:
        """
        วิธีใหม่ในการหา breakout ใน Linear Regression Channel ตามที่ต้องการ:
        1. Load data 120 timeframes จาก Binance (ทำใน enhanced_position_manager.py แล้ว)
        2. วน loop 10 รอบ จากชั่วโมงก่อนหน้า
        3. ส่งให้ Linear Regression Channel ดูว่า breakout หรือไม่
        4. ถ้า breakout ก็จบ loop ทันที
        """
        if len(self.data) < self.length:
            return {'has_breakout': False, 'reason': 'insufficient_data', 'candles_ago': 0}
        
        print(f"        🔄 เริ่มวิเคราะห์ LRC breakout (วน loop 10 รอบ จากชั่วโมงก่อนหน้า)...")
        
        # วน loop 10 รอบ จากชั่วโมงก่อนหน้า
        for i in range(1, min(max_lookback + 1, len(self.data))):
            print(f"        🔍 Loop รอบที่ {i}: ตรวจสอบ breakout ที่แท่งเทียน {i} ย้อนหลัง...")
            
            # สร้าง dataset สำหรับแท่งเทียนที่ i ย้อนหลัง
            # ใช้ข้อมูล length แท่งเทียน ณ จุดนั้น
            end_index = len(self.data) - i
            start_index = max(0, end_index - self.length)
            
            if end_index - start_index < self.length:
                continue  # ข้อมูลไม่เพียงพอ
            
            # ดึงข้อมูลสำหรับการคำนวณ LRC ณ จุดนั้น
            historical_data = self.data[start_index:end_index]
            close_prices = [candle.close for candle in historical_data]
            
            # คำนวณ Linear Regression Channel สำหรับจุดนั้น
            intercept, endy, dev, slope = self.get_channel(close_prices, len(close_prices))
            
            if dev == 0:
                continue  # ข้าม deviation = 0
            
            # คำนวณ channel lines ณ จุดนั้น
            y2_ = endy
            upper_channel = y2_ + dev * self.deviation
            lower_channel = y2_ - dev * self.deviation
            
            # ราคา close ณ จุดนั้น
            current_close = historical_data[-1].close
            
            # ตรวจสอบ breakout ตาม PineScript logic
            breakout_found = False
            breakout_direction = ""
            
            if slope > 0 and current_close < lower_channel:
                # Downward breakout in uptrend
                breakout_found = True
                breakout_direction = "DOWN"
                print(f"        ✅ พบ DOWN breakout ที่แท่งเทียน {i} ย้อนหลัง!")
                print(f"        📊 Close: {current_close:.6f} < Lower: {lower_channel:.6f} (Slope: {slope:.6f})")
            elif slope < 0 and current_close > upper_channel:
                # Upward breakout in downtrend  
                breakout_found = True
                breakout_direction = "UP"
                print(f"        ✅ พบ UP breakout ที่แท่งเทียน {i} ย้อนหลัง!")
                print(f"        📊 Close: {current_close:.6f} > Upper: {upper_channel:.6f} (Slope: {slope:.6f})")
            
            # ถ้าเจอ breakout ก็จบ loop ทันที
            if breakout_found:
                return {
                    'has_breakout': True,
                    'direction': breakout_direction,
                    'candles_ago': i,
                    'slope': slope,
                    'upper_channel': upper_channel,
                    'middle_line': y2_,
                    'lower_channel': lower_channel,
                    'deviation': dev,
                    'trend_direction': "UP" if slope > 0 else "DOWN" if slope < 0 else "SIDEWAYS",
                    'close_price': current_close
                }
            else:
                print(f"        ❌ ไม่พบ breakout ที่แท่งเทียน {i} ย้อนหลัง")
                print(f"        📊 Close: {current_close:.6f}, Upper: {upper_channel:.6f}, Lower: {lower_channel:.6f}")
        
        # ไม่พบ breakout ในทุกรอบ
        print(f"        ❌ ไม่พบ breakout ในทั้ง {max_lookback} แท่งเทียนย้อนหลัง")
        return {
            'has_breakout': False,
            'direction': "",
            'candles_ago': 0,
            'slope': 0,
            'upper_channel': 0,
            'middle_line': 0,
            'lower_channel': 0,
            'deviation': 0,
            'trend_direction': "SIDEWAYS",
            'reason': 'no_breakout_found'
        }

    def _detect_lrc_breakout(self, max_lookback: int) -> Dict[str, Any]:
        """
        ตรวจสอบ LRC breakout ตาม PineScript logic อย่างเคร่งคลัด
        PineScript: outofchannel = (slope > 0 and close < y2_ - dev * devlen) ? 0 : (slope < 0 and close > y2_ + dev * devlen) ? 2 : -1
        """
        # Use close prices for regression (src = close ใน PineScript)
        close_prices = [candle.close for candle in self.data]
        
        # Calculate channel for current period (ตาม PineScript get_channel function)
        intercept, endy, dev, slope = self.get_channel(close_prices, self.length)
        
        if dev == 0:
            return {'has_breakout': False, 'reason': 'zero_deviation'}
            
        # Calculate channel lines exactly like PineScript
        # y2_ = endy (end value of regression line)
        y2_ = endy
        upper_channel = y2_ + dev * self.deviation  # y2_ + dev * devlen
        lower_channel = y2_ - dev * self.deviation  # y2_ - dev * devlen
        
        # ตรวจสอบ breakout ใน 10 timeframes ย้อนหลัง ตาม PineScript outofchannel logic
        breakout_found = False
        breakout_direction = ""
        breakout_candles_ago = 0  # เปลี่ยนจาก 999 เป็น 0
        
        for i in range(1, min(max_lookback + 1, len(self.data))):
            candle = self.data[-i]  # ย้อนหลัง i แท่งเทียน
            current_close = candle.close
            
            # คำนวณ channel values สำหรับแท่งเทียนย้อนหลัง
            # ใน PineScript จะใช้ current slope และ dev แต่คำนวณ position ย้อนหลัง
            historical_y2 = intercept + slope * (self.length - 1 - (i - 1))  # y2_ สำหรับแท่งเทียนนั้น
            historical_upper = historical_y2 + dev * self.deviation
            historical_lower = historical_y2 - dev * self.deviation
            
            # PineScript outofchannel logic:
            # outofchannel = (slope > 0 and close < y2_ - dev * devlen) ? 0 : (slope < 0 and close > y2_ + dev * devlen) ? 2 : -1
            outofchannel = -1  # default: no breakout
            
            if slope > 0 and current_close < historical_lower:
                # Downward breakout in uptrend (outofchannel = 0)
                outofchannel = 0
                breakout_found = True
                breakout_direction = "DOWN"
                breakout_candles_ago = i
                break
            elif slope < 0 and current_close > historical_upper:
                # Upward breakout in downtrend (outofchannel = 2)
                outofchannel = 2
                breakout_found = True
                breakout_direction = "UP"
                breakout_candles_ago = i
                break
            # Note: PineScript ไม่มี case สำหรับ sideways trend ใน outofchannel logic
        
        return {
            'has_breakout': breakout_found,
            'direction': breakout_direction,
            'candles_ago': breakout_candles_ago,
            'slope': slope,
            'upper_channel': upper_channel,
            'middle_line': y2_,  # y2_ จาก PineScript
            'lower_channel': lower_channel,
            'deviation': dev,
            'trend_direction': "UP" if slope > 0 else "DOWN" if slope < 0 else "SIDEWAYS"
        }
    
    def _check_ema7_cross_confirmation(self) -> Dict[str, Any]:
        """
        Function ใหม่: ตรวจสอบว่า 2 แท่งเทียนล่าสุดทับ EMA7 หรือไม่
        Returns: dict with cross information
        """
        if len(self.data) < self.ema7_period + 2:
            return {'has_cross': False, 'reason': 'insufficient_data'}
            
        ema_values = self.calculate_ema7()
        if len(ema_values) < 2:
            return {'has_cross': False, 'reason': 'insufficient_ema_data'}
            
        # Get latest 2 candles and their EMA7 values
        candle1 = self.data[-1]  # แท่งเทียนล่าสุด
        candle2 = self.data[-2]  # แท่งเทียนก่อนหน้า
        ema7_1 = ema_values[-1]  # EMA7 ล่าสุด
        ema7_2 = ema_values[-2]  # EMA7 ก่อนหน้า
        
        # ตรวจสอบว่าแท่งเทียนทับ EMA7 หรือไม่
        candle1_crosses = (
            (candle1.low <= ema7_1 <= candle1.high) or  # EMA7 อยู่ในช่วง high-low
            (min(candle1.open, candle1.close) <= ema7_1 <= max(candle1.open, candle1.close))  # EMA7 อยู่ในตัวเทียน
        )
        
        candle2_crosses = (
            (candle2.low <= ema7_2 <= candle2.high) or  # EMA7 อยู่ในช่วง high-low
            (min(candle2.open, candle2.close) <= ema7_2 <= max(candle2.open, candle2.close))  # EMA7 อยู่ในตัวเทียน
        )
        
        # ต้องมีอย่างน้อย 1 แท่งเทียนที่ทับ EMA7
        has_cross = candle1_crosses or candle2_crosses
        
        cross_description = ""
        if candle1_crosses and candle2_crosses:
            cross_description = "both_candles_cross_ema7"
        elif candle1_crosses:
            cross_description = "latest_candle_cross_ema7"
        elif candle2_crosses:
            cross_description = "previous_candle_cross_ema7"
        else:
            cross_description = "no_ema7_cross"
        
        return {
            'has_cross': has_cross,
            'description': cross_description,
            'candle1_crosses': candle1_crosses,
            'candle2_crosses': candle2_crosses,
            'ema7_latest': ema7_1,
            'ema7_previous': ema7_2
        }
    
    def _create_confirmed_signal(self, lrc_result: Dict[str, Any], ema25_result: Dict[str, Any]) -> LRCResult:
        """
        สร้าง signal ที่ผ่านการยืนยันทั้ง LRC breakout และ EMA25 cross
        พร้อมส่งให้ AI ตัดสินใจสุดท้าย
        """
        # กำหนด pattern type และ signal direction
        if lrc_result['direction'] == "UP":
            pattern_type = "LRC_BREAKOUT_UP_EMA25_CONFIRMED"
            signal = "LONG"
        elif lrc_result['direction'] == "DOWN":
            pattern_type = "LRC_BREAKOUT_DOWN_EMA25_CONFIRMED"
            signal = "SHORT"
        else:
            pattern_type = "NO_CLEAR_SIGNAL"
            signal = "NEUTRAL"
        
        # คำนวณ confidence based on breakout quality และ EMA25 confirmation
        confidence = self._calculate_confirmed_confidence(lrc_result, ema25_result)
        
        # คำนวณ entry/exit levels
        current_price = self.data[-1].close
        entry_level = current_price
        
        # กำหนด stop loss และ take profit
        if signal == "LONG":
            stop_loss = lrc_result['lower_channel'] * 0.995  # 0.5% below support
            take_profit = lrc_result['upper_channel'] * 1.02  # fallback: 2% above upper channel (AI จะปรับด้วย Fibonacci)
        elif signal == "SHORT":
            stop_loss = lrc_result['upper_channel'] * 1.005  # 0.5% above resistance
            take_profit = lrc_result['lower_channel'] * 0.98  # fallback: 2% below lower channel (AI จะปรับด้วย Fibonacci)
        else:
            stop_loss = current_price * 0.95  # 5% fallback
            take_profit = current_price * 1.15  # 15% fallback
        
        # สร้าง description
        description = f"LRC {lrc_result['trend_direction']} breakout {lrc_result['candles_ago']} candles ago + EMA25 {ema25_result['description']} (TP=AI_FIBONACCI)"
        
        return LRCResult(
            pattern_type=pattern_type,
            confidence=confidence,
            signal=signal,
            strength=min(confidence / 10, 10),
            entry_level=entry_level,
            stop_loss=stop_loss,
            take_profit=take_profit,
            volume_confirm=self._check_volume_confirmation(lrc_result['candles_ago']),
            pattern_status="CONFIRMED_SIGNAL",
            description=description,
            upper_channel=lrc_result['upper_channel'],
            middle_line=lrc_result['middle_line'],
            lower_channel=lrc_result['lower_channel'],
            slope=lrc_result['slope'],
            deviation=lrc_result['deviation'],
            trend_direction=lrc_result['trend_direction'],
            breakout_candles_ago=lrc_result['candles_ago'],
            is_fresh_breakout=True  # ผ่านการยืนยันแล้ว
        )
    
    def _calculate_confirmed_confidence(self, lrc_result: Dict[str, Any], ema25_result: Dict[str, Any]) -> float:
        """คำนวณ confidence สำหรับ signal ที่ได้รับการยืนยัน"""
        confidence = 0.0
        
        # LRC breakout freshness (ใหม่มากแค่ไหน)
        candles_ago = lrc_result['candles_ago']
        if candles_ago <= 2:
            confidence += 30
        elif candles_ago <= 5:
            confidence += 25
        elif candles_ago <= 10:
            confidence += 20
        
        # EMA25 cross confirmation
        if ema25_result['candle1_crosses'] and ema25_result['candle2_crosses']:
            confidence += 25  # ทั้ง 2 แท่งทับ EMA25
        elif ema25_result['candle1_crosses'] or ema25_result['candle2_crosses']:
            confidence += 20  # มี 1 แท่งทับ EMA25
        
        # Slope strength
        slope_strength = abs(lrc_result['slope'])
        slope_score = min(slope_strength * 1000, 15)  # Scale and cap at 15
        confidence += slope_score
        
        # Base confirmation bonus
        confidence += 20  # ผ่านการยืนยันทั้ง 2 เงื่อนไข
        
        return min(confidence, 100.0)
    
    def _check_volume_confirmation(self, breakout_candles_ago: int) -> bool:
        """Check if there was volume spike during breakout"""
        if breakout_candles_ago >= len(self.data) or breakout_candles_ago <= 0:
            return False
            
        # Get volume at breakout candle
        breakout_volume = self.data[-breakout_candles_ago].volume
        
        # Calculate average volume (last 10 candles before breakout)
        start_idx = max(0, len(self.data) - breakout_candles_ago - 10)
        end_idx = len(self.data) - breakout_candles_ago
        
        if end_idx <= start_idx:
            return False
            
        avg_volume = sum(candle.volume for candle in self.data[start_idx:end_idx]) / (end_idx - start_idx)
        
        # Volume spike: breakout volume > 150% of average
        return breakout_volume > avg_volume * 1.5
    
    def _calculate_confidence(self, breakout_found: bool, candles_ago: int, 
                            volume_confirm: bool, slope_strength: float) -> float:
        """Calculate confidence score for the signal"""
        if not breakout_found:
            return 15.0  # Low confidence for no breakout
            
        confidence = 0.0
        
        # Breakout freshness (more recent = higher score)
        if candles_ago <= 2:
            confidence += 40
        elif candles_ago <= 4:
            confidence += 30
        elif candles_ago <= 7:
            confidence += 20
        else:
            confidence += 10
            
        # Volume confirmation
        if volume_confirm:
            confidence += 25
        else:
            confidence += 10
            
        # Slope strength (stronger trend = higher confidence)
        slope_score = min(abs(slope_strength) * 1000, 20)  # Scale and cap at 20
        confidence += slope_score
        
        # Base pattern recognition
        confidence += 15
        
        return min(confidence, 100.0)
    
    def _no_signal(self, reason: str = "no_signal") -> LRCResult:
        """Return no signal result"""
        current_price = self.data[-1].close if self.data else 0.0
        
        return LRCResult(
            pattern_type="NO_BREAKOUT",
            confidence=15.0,
            signal="NEUTRAL",
            strength=1.5,
            entry_level=current_price,
            stop_loss=current_price * 0.95,
            take_profit=current_price * 1.15,
            volume_confirm=False,
            pattern_status="NO_BREAKOUT",
            description=f"No Linear Regression Channel signal: {reason}",
            upper_channel=0.0,
            middle_line=0.0,
            lower_channel=0.0,
            slope=0.0,
            deviation=0.0,
            trend_direction="SIDEWAYS",
            breakout_candles_ago=0,  # เปลี่ยนจาก 999 เป็น 0
            is_fresh_breakout=False
        )
        
    def calculate_ema7(self) -> List[float]:
        """Calculate 7-period Exponential Moving Average"""
        if len(self.data) < self.ema7_period:
            return []
            
        ema_values = []
        alpha = 2 / (self.ema7_period + 1)  # EMA smoothing factor
        
        # Initialize with first close price
        ema = self.data[0].close
        ema_values.append(ema)
        
        # Calculate EMA for remaining periods
        for i in range(1, len(self.data)):
            ema = alpha * self.data[i].close + (1 - alpha) * ema
            ema_values.append(ema)
            
        return ema_values

    def _create_confirmed_signal_from_lrc_only(self, lrc_result: Dict[str, Any]) -> LRCResult:
        """
        สร้าง signal จาก LRC breakout เท่านั้น (ไม่ต้องยืนยัน EMA25)
        วิธีใหม่: วน loop 10 รอบ → ตรวจสอบ LRC breakout → ส่งให้ AI
        """
        # กำหนด pattern type และ signal direction
        if lrc_result['direction'] == "UP":
            pattern_type = "LRC_BREAKOUT_UP"
            signal = "LONG"
        elif lrc_result['direction'] == "DOWN":
            pattern_type = "LRC_BREAKOUT_DOWN"
            signal = "SHORT"
        else:
            pattern_type = "NO_CLEAR_SIGNAL"
            signal = "NEUTRAL"
        
        # คำนวณ confidence based on breakout quality เท่านั้น
        confidence = self._calculate_lrc_only_confidence(lrc_result)
        
        # คำนวณ entry/exit levels
        current_price = self.data[-1].close
        entry_level = current_price
        
        # กำหนด stop loss และ take profit
        if signal == "LONG":
            stop_loss = lrc_result['lower_channel'] * 0.995  # 0.5% below support
            take_profit = lrc_result['upper_channel'] * 1.02  # fallback: 2% above upper channel (AI จะปรับด้วย Fibonacci)
        elif signal == "SHORT":
            stop_loss = lrc_result['upper_channel'] * 1.005  # 0.5% above resistance
            take_profit = lrc_result['lower_channel'] * 0.98  # fallback: 2% below lower channel (AI จะปรับด้วย Fibonacci)
        else:
            stop_loss = current_price * 0.95  # 5% fallback
            take_profit = current_price * 1.15  # 15% fallback
        
        # สร้าง description (เฉพาะ LRC)
        description = f"LRC {lrc_result['trend_direction']} breakout {lrc_result['candles_ago']} candles ago (TP=AI_FIBONACCI)"
        
        return LRCResult(
            pattern_type=pattern_type,
            confidence=confidence,
            signal=signal,
            strength=min(confidence / 10, 10),
            entry_level=entry_level,
            stop_loss=stop_loss,
            take_profit=take_profit,
            volume_confirm=self._check_volume_confirmation(lrc_result['candles_ago']),
            pattern_status="CONFIRMED_SIGNAL",
            description=description,
            upper_channel=lrc_result['upper_channel'],
            middle_line=lrc_result['middle_line'],
            lower_channel=lrc_result['lower_channel'],
            slope=lrc_result['slope'],
            deviation=lrc_result['deviation'],
            trend_direction=lrc_result['trend_direction'],
            breakout_candles_ago=lrc_result['candles_ago'],
            is_fresh_breakout=True  # ยืนยันจาก LRC breakout แล้ว
        )

    def _calculate_lrc_only_confidence(self, lrc_result: Dict[str, Any]) -> float:
        """
        คำนวณ confidence สำหรับ LRC breakout เท่านั้น (ไม่รวม EMA25)
        """
        base_confidence = 65.0  # confidence เริ่มต้นสำหรับ LRC breakout
        
        # ปรับ confidence ตาม slope strength
        slope_strength = abs(lrc_result['slope'])
        if slope_strength > 0.01:
            base_confidence += 10.0  # slope แรง
        elif slope_strength > 0.005:
            base_confidence += 5.0   # slope ปานกลาง
        
        # ปรับ confidence ตาม deviation
        if lrc_result['deviation'] > 0:
            # deviation ยิ่งสูง แสดงว่า channel ยิ่งกว้าง = breakout มีนัยสำคัญมากขึ้น
            dev_factor = min(lrc_result['deviation'] * 100, 15.0)
            base_confidence += dev_factor
        
        # ปรับ confidence ตามระยะเวลาที่เกิด breakout
        if lrc_result['candles_ago'] <= 3:
            base_confidence += 5.0  # breakout ใหม่มาก
        elif lrc_result['candles_ago'] <= 5:
            base_confidence += 2.0  # breakout ใหม่พอควร
        
        return min(base_confidence, 95.0)  # จำกัดไม่เกิน 95%

    def _validate_ema7_for_breakout_direction(self, breakout_direction: str) -> Dict[str, Any]:
        """
        ตรวจสอบ EMA7 ตามทิศทาง breakout:
        - breakout UP: ตรวจ 3 แท่งล่าสุดทับ EMA7 → ราคาล่าสุด > EMA7
        - ถ้า breakout DOWN: ตรวจ 3 แท่งล่าสุดทับ EMA7 → ราคาล่าสุด < EMA7
        """
        if len(self.data) < self.ema7_period + 3:
            return {'is_valid': False, 'reason': 'insufficient_data_for_ema7'}
        
        # คำนวณ EMA7
        ema_values = self.calculate_ema7()
        if len(ema_values) < 3:
            return {'is_valid': False, 'reason': 'insufficient_ema_data'}
        
        # ตรวจสอบ 3 แท่งเทียนล่าสุดว่าทับ EMA7 หรือไม่
        has_ema7_touch = False
        touched_candle_info = None
        
        for i in range(3):  # 0, 1, 2 (ล่าสุด, ก่อนหน้า 1, ก่อนหน้า 2)
            candle_index = len(self.data) - 1 - i
            
            if candle_index < 0 or candle_index >= len(self.data):
                continue
                
            candle = self.data[candle_index]
            ema7 = ema_values[candle_index]
            
            # ตรวจสอบว่าแท่งเทียนทับ EMA7 หรือไม่
            candle_touches_ema7 = (
                (candle.low <= ema7 <= candle.high) or  # EMA7 อยู่ในช่วง high-low
                (min(candle.open, candle.close) <= ema7 <= max(candle.open, candle.close))  # EMA7 อยู่ในตัวเทียน
            )
            
            if candle_touches_ema7:
                has_ema7_touch = True
                candle_position = "ล่าสุด" if i == 0 else f"ก่อนหน้า {i}"
                touched_candle_info = {
                    'position': candle_position,
                    'candle_index': candle_index,
                    'ema7_value': ema7
                }
                print(f"        ✅ พบแท่งเทียน{candle_position}ทับ EMA7 (EMA7: {ema7:.6f})")
                break
        
        if not has_ema7_touch:
            print(f"        ❌ ไม่พบแท่งเทียนใดทับ EMA7 ใน 3 แท่งล่าสุด")
            return {'is_valid': False, 'reason': 'no_ema7_touch_in_last_3_candles'}
        
        # ตรวจสอบราคาปัจจุบันเทียบกับ EMA7 ตามทิศทาง breakout
        current_price = self.data[-1].close
        current_ema7 = ema_values[-1]
        
        if breakout_direction == "UP":
            # breakout UP: ราคาล่าสุดต้องสูงกว่า EMA7
            price_condition = current_price > current_ema7
            condition_text = f"ราคาล่าสุด ({current_price:.6f}) > EMA7 ({current_ema7:.6f})"
            
            if price_condition:
                print(f"        ✅ {condition_text} - ผ่าน!")
            else:
                print(f"        ❌ {condition_text} - ไม่ผ่าน!")
                return {'is_valid': False, 'reason': 'price_below_ema7_for_up_breakout'}
                
        elif breakout_direction == "DOWN":
            # breakout DOWN: ราคาล่าสุดต้องต่ำกว่า EMA7
            price_condition = current_price < current_ema7
            condition_text = f"ราคาล่าสุด ({current_price:.6f}) < EMA7 ({current_ema7:.6f})"
            
            if price_condition:
                print(f"        ✅ {condition_text} - ผ่าน!")
            else:
                print(f"        ❌ {condition_text} - ไม่ผ่าน!")
                return {'is_valid': False, 'reason': 'price_above_ema7_for_down_breakout'}
        else:
            return {'is_valid': False, 'reason': 'unknown_breakout_direction'}
        
        return {
            'is_valid': True,
            'breakout_direction': breakout_direction,
            'current_price': current_price,
            'current_ema7': current_ema7,
            'ema7_touch_info': touched_candle_info,
            'stop_loss_level': current_ema7  # Stop Loss = EMA7
        }

    def _create_confirmed_signal_from_lrc_with_ema7(self, lrc_result: Dict[str, Any], ema7_result: Dict[str, Any]) -> LRCResult:
        """
        สร้าง signal จาก LRC breakout + EMA7 validation
        Stop Loss = EMA7
        """
        breakout_direction = lrc_result['direction']
        
        # กำหนด pattern type และ signal direction
        if breakout_direction == "UP":
            pattern_type = "LRC_BREAKOUT_UP_EMA7_VALIDATED"
            signal = "LONG"
        elif breakout_direction == "DOWN":
            pattern_type = "LRC_BREAKOUT_DOWN_EMA7_VALIDATED"
            signal = "SHORT"
        else:
            pattern_type = "NO_CLEAR_SIGNAL"
            signal = "NEUTRAL"
        
        # คำนวณ confidence based on breakout quality และ EMA7 validation
        confidence = self._calculate_lrc_ema7_confidence(lrc_result, ema7_result)
        
        # ใช้ EMA7 เป็น Stop Loss ตามที่ต้องการ
        current_price = ema7_result['current_price']
        ema7_level = ema7_result['current_ema7']
        entry_level = current_price
        stop_loss = ema7_level  # Stop Loss = EMA7
        
        # กำหนด take profit ให้ AI หาด้วย Fibonacci levels (ใช้ fallback เพื่อ validation)
        if signal == "LONG":
            # Ensure take profit is always above current price for LONG
            channel_based_tp = lrc_result['upper_channel'] * 1.02
            price_based_tp = current_price * 1.02  # minimum 2% above current price
            take_profit = max(channel_based_tp, price_based_tp)  # use whichever is higher
        elif signal == "SHORT":
            # Ensure take profit is always below current price for SHORT
            channel_based_tp = lrc_result['lower_channel'] * 0.98
            price_based_tp = current_price * 0.98  # minimum 2% below current price
            take_profit = min(channel_based_tp, price_based_tp)  # use whichever is lower
        else:
            take_profit = current_price * (1.15 if signal == "LONG" else 0.85)  # fallback
        
        # สร้าง description
        description = f"LRC {breakout_direction} breakout + EMA7 validation (SL=EMA7, TP=AI_FIBONACCI)"
        
        return LRCResult(
            pattern_type=pattern_type,
            confidence=confidence,
            signal=signal,
            strength=min(confidence / 10, 10),
            entry_level=entry_level,
            stop_loss=stop_loss,  # Stop Loss = EMA7
            take_profit=take_profit,
            volume_confirm=self._check_volume_confirmation(lrc_result['candles_ago']),
            pattern_status="CONFIRMED_SIGNAL",
            description=description,
            upper_channel=lrc_result['upper_channel'],
            middle_line=lrc_result['middle_line'],
            lower_channel=lrc_result['lower_channel'],
            slope=lrc_result['slope'],
            deviation=lrc_result['deviation'],
            trend_direction=lrc_result['trend_direction'],
            breakout_candles_ago=lrc_result['candles_ago'],
            is_fresh_breakout=True  # ผ่านการยืนยันแล้ว
        )

    def _calculate_lrc_ema7_confidence(self, lrc_result: Dict[str, Any], ema7_result: Dict[str, Any]) -> float:
        """
        คำนวณ confidence สำหรับ LRC breakout + EMA7 validation
        """
        base_confidence = 70.0  # confidence เริ่มต้น
        
        # ปรับ confidence ตาม slope strength
        slope_strength = abs(lrc_result['slope'])
        if slope_strength > 0.01:
            base_confidence += 15.0  # slope แรง
        elif slope_strength > 0.005:
            base_confidence += 8.0   # slope ปานกลาง
        
        # ปรับ confidence ตาม deviation (channel width)
        if lrc_result['deviation'] > 0:
            dev_factor = min(lrc_result['deviation'] * 100, 10.0)
            base_confidence += dev_factor
        
        # ปรับ confidence ตามระยะเวลาที่เกิด breakout
        if lrc_result['candles_ago'] <= 3:
            base_confidence += 10.0  # breakout ใหม่มาก
        elif lrc_result['candles_ago'] <= 5:
            base_confidence += 5.0   # breakout ใหม่พอควร
        
        # ปรับ confidence ตามความแข็งแกร่งของ EMA7 validation
        price_ema_ratio = abs(ema7_result['current_price'] - ema7_result['current_ema7']) / ema7_result['current_ema7']
        if price_ema_ratio > 0.02:  # ราคาห่างจาก EMA7 มากกว่า 2%
            base_confidence += 5.0
        
        return min(base_confidence, 95.0)  # จำกัดไม่เกิน 95%

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Linear Regression Channel Pattern Detector')
    parser.add_argument('--data', type=str, help='JSON data string')
    parser.add_argument('--length', type=int, default=100, help='LRC length (default: 100)')
    parser.add_argument('--deviation', type=float, default=2.0, help='LRC deviation (default: 2.0)')
    
    args = parser.parse_args()
    
    if not args.data:
        print("Error: --data parameter is required")
        sys.exit(1)
    
    try:
        data_json = json.loads(args.data)
        
        # Convert to OHLCV objects
        ohlcv_data = []
        for item in data_json:
            ohlcv = OHLCV(
                timestamp=item[0],
                open=float(item[1]),
                high=float(item[2]),
                low=float(item[3]),
                close=float(item[4]),
                volume=float(item[5])
            )
            ohlcv_data.append(ohlcv)
        
        # Create detector and analyze
        detector = LinearRegressionChannelDetector(ohlcv_data, args.length, args.deviation)
        result = detector.detect_breakout_with_ema7_confirmation()
        
        # Convert to output format for AI
        output = {
            "pattern_detected": result.pattern_type,
            "signal": result.signal,
            "confidence": result.confidence,
            "slope": result.slope,
            "trend_direction": result.trend_direction,
            "breakout_candles_ago": result.breakout_candles_ago,
            "is_fresh_breakout": result.is_fresh_breakout,
            "volume_confirm": result.volume_confirm,
            "upper_channel": result.upper_channel,
            "middle_line": result.middle_line,
            "lower_channel": result.lower_channel,
            "entry_level": result.entry_level,
            "stop_loss": result.stop_loss,
            "take_profit": result.take_profit,
            "description": result.description
        }
        
        print(json.dumps(output))
        
    except Exception as e:
        error_output = {
            "pattern_detected": "ERROR",
            "signal": "NEUTRAL",
            "confidence": 0.0,
            "error": str(e)
        }
        print(json.dumps(error_output))
        sys.exit(1)


if __name__ == "__main__":
    main()
