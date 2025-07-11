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
import os
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import argparse


def ensure_historical_data_cache():
    """สร้างโฟลเดอร์ historical_data_cache และไฟล์ตัวอย่างถ้าไม่มี"""
    cache_dir = "historical_data_cache"
    sample_file = os.path.join(cache_dir, "BTC_USDT_USDT_1h.json")
    
    # สร้างโฟลเดอร์ถ้าไม่มี
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        print(f"✅ สร้างโฟลเดอร์ {cache_dir}")
    
    # สร้างไฟล์ตัวอย่างถ้าไม่มี
    if not os.path.exists(sample_file):
        print(f"📊 สร้างไฟล์ข้อมูลตัวอย่าง {sample_file}")
        create_sample_data(sample_file)
        
    return sample_file


def ensure_all_required_folders():
    """สร้างโฟลเดอร์ทั้งหมดที่จำเป็นสำหรับระบบ"""
    required_folders = [
        "historical_data_cache",    # เก็บข้อมูล OHLCV cache
        "temp",                     # เก็บไฟล์ชั่วคราว
        "configs"                   # เก็บ configuration files
    ]
    
    created_folders = []
    
    for folder in required_folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            created_folders.append(folder)
            print(f"✅ สร้างโฟลเดอร์ {folder}")
    
    if created_folders:
        print(f"📁 สร้างโฟลเดอร์ใหม่ทั้งหมด: {len(created_folders)} โฟลเดอร์")
    else:
        print("📁 โฟลเดอร์ทั้งหมดมีอยู่แล้ว")
    
    # สร้างไฟล์ตัวอย่างใน historical_data_cache
    sample_file = ensure_historical_data_cache()
    
    # สร้างไฟล์ config ตัวอย่างถ้าไม่มี
    create_sample_config_files()
    
    return sample_file


def create_sample_config_files():
    """สร้างไฟล์ config ตัวอย่างถ้าไม่มี"""
    configs = {
        "configs/trading_config.json": {
            "position_size_usdt": 100,
            "max_positions": 99999,
            "use_all_capital": True,
            "unlimited_capital": True,
            "total_capital_usdt": 999999999,
            "save_history": False,
            "save_reports": False,
            "save_logs": False,
            "risk_percentage": 2.0,
            "lrc_length": 100,
            "lrc_deviation": 2.0,
            "max_lookback": 5,
            "min_confidence": 75.0
        },
        "configs/symbols_config.json": {
            "active_symbols": [
                "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT",
                "DOTUSDT", "LINKUSDT", "LTCUSDT", "BCHUSDT", "XLMUSDT"
            ],
            "excluded_symbols": [],
            "min_volume_24h": 1000000
        },
        "configs/ai_config.json": {
            "api_provider": "deepseek",
            "model": "deepseek-chat",
            "api_url": "https://api.deepseek.com/v1/chat/completions",
            "max_tokens": 1000,
            "temperature": 0.1,
            "timeout": 30
        }
    }
    
    for config_file, config_data in configs.items():
        if not os.path.exists(config_file):
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"📄 สร้างไฟล์ config: {config_file}")


def create_sample_log_structure():
    """ไม่สร้าง log files เนื่องจากปิดการเก็บประวัติ"""
    print("📝 ปิดการเก็บ log files (save_logs: false)")
    pass


def create_readme_files():
    """สร้างไฟล์ README สำหรับแต่ละโฟลเดอร์"""
    readme_contents = {
        "historical_data_cache/README.md": """# Historical Data Cache

โฟลเดอร์นี้เก็บข้อมูล OHLCV ที่ดึงมาจาก Exchange

## โครงสร้างไฟล์:
- `{SYMBOL}_USDT_{TIMEFRAME}.json` - ข้อมูล OHLCV ของเหรียญแต่ละตัว

## รูปแบบข้อมูล:
```json
[
  [timestamp, open, high, low, close, volume],
  ...
]
```
""",
        "configs/README.md": """# Configuration Files

โฟลเดอร์นี้เก็บไฟล์ configuration

## ไฟล์ config:
- `trading_config.json` - การตั้งค่าการเทรด
- `symbols_config.json` - การตั้งค่าเหรียญ
- `ai_config.json` - การตั้งค่า AI

## trading_config.json Parameters:
- `position_size_usdt`: ขนาด position ต่อครั้ง (100 USDT)
- `max_positions`: จำนวน position สูงสุด (99999 = ไม่จำกัด)
- `use_all_capital`: ใช้เงินทุนหมด (true/false)
- `unlimited_capital`: เปิด position ไม่จำกัดเงิน (true/false)
- `total_capital_usdt`: เงินทุนทั้งหมด (999999999 USDT = ไม่จำกัด)
- `save_history`: เก็บประวัติการเทรด (false = ไม่เก็บ)
- `save_reports`: เก็บรายงานการเทรด (false = ไม่เก็บ)
- `save_logs`: เก็บ log files (false = ไม่เก็บ)
- `risk_percentage`: เปอร์เซ็นต์ความเสี่ยง (2%)
- `lrc_length`: ความยาว Linear Regression Channel (100)
- `lrc_deviation`: ค่าเบี่ยงเบน channel (2.0)
- `max_lookback`: จำนวนแท่งเทียนย้อนหลัง (5)
- `min_confidence`: ความเชื่อมั่นขั้นต่ำ (75%)

## ai_config.json Parameters:
- `api_provider`: ผู้ให้บริการ AI (deepseek)
- `model`: โมเดล AI (deepseek-chat)
- `api_url`: URL ของ DeepSeek API
- `max_tokens`: จำนวน token สูงสุด (1000)
- `temperature`: ความสร้างสรรค์ของ AI (0.1)
- `timeout`: Timeout สำหรับ API call (30 วินาที)

## วิธีใช้เงินไม่จำกัด:
เมื่อ `unlimited_capital: true` ระบบจะ:
1. เปิด position ไม่จำกัดจำนวน
2. ไม่ตรวจสอบเงินทุนที่เหลือ
3. เปิด position ทุกครั้งที่มี signal
4. ไม่สนใจ max_positions และ total_capital_usdt

## การปิดประวัติและรายงาน:
เมื่อ save_history, save_reports, save_logs = false ระบบจะ:
1. ไม่เก็บประวัติการเทรด
2. ไม่สร้างรายงาน
3. ไม่เขียน log files
4. ประหยัดพื้นที่ดิสก์และทำให้ระบบเร็วขึ้น
""",
        "temp/README.md": """# Temporary Files

โฟลเดอร์นี้เก็บไฟล์ชั่วคราวที่ใช้ในการประมวลผล

## การใช้งาน:
- ไฟล์ในโฟลเดอร์นี้อาจถูกลบอัตโนมัติ
- ใช้สำหรับการประมวลผลข้อมูลชั่วคราว
"""
    }
    
    for readme_file, content in readme_contents.items():
        if not os.path.exists(readme_file):
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📖 สร้างไฟล์ README: {readme_file}")


def create_sample_data(file_path: str):
    """สร้างข้อมูล OHLCV ตัวอย่างสำหรับทดสอบ"""
    # สร้างข้อมูล BTC ตัวอย่าง 120 แท่งเทียน
    import time
    current_time = int(time.time() * 1000)
    base_price = 45000.0
    
    sample_data = []
    for i in range(120):
        timestamp = current_time - (119 - i) * 3600000  # 1 hour intervals
        
        # สร้างราคาที่มี uptrend
        trend_factor = i * 15  # เพิ่มขึ้นเรื่อยๆ
        
        open_price = base_price + trend_factor
        close_price = open_price + 50  # close สูงกว่า open (green candles)
        high_price = close_price + 100
        low_price = open_price - 50
        volume = 1000 + (i % 100) * 10
        
        # สร้าง breakout UP ที่แท่งที่ 117 (3 candles ago) ให้ชัดเจน
        if i == 117:
            # ทำให้ high และ close สูงมากเพื่อ breakout channel
            breakout_boost = 2000
            high_price = close_price + breakout_boost
            close_price = open_price + breakout_boost
            print(f"🎯 สร้าง breakout candle ที่ index {i}: Close={close_price}, High={high_price} (3 candles ago)")
        
        sample_data.append([
            int(timestamp),           # timestamp as integer
            float(round(open_price, 2)),   # open as float
            float(round(high_price, 2)),   # high as float  
            float(round(low_price, 2)),    # low as float
            float(round(close_price, 2)),  # close as float
            float(round(volume, 2))        # volume as float
        ])
    
    # เขียนไฟล์
    with open(file_path, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"✅ สร้างข้อมูลตัวอย่าง {len(sample_data)} แท่งเทียน")
    print(f"📈 ข้อมูลมี uptrend + breakout UP ที่ candle 117 (3 candles ago)")
    print(f"📊 ราคาล่าสุด: {sample_data[-1][4]}")  # แสดงราคา close ล่าสุด


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
            
        # ขั้นตอนที่ 1: วน loop 5 รอบ หา LRC breakout
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
        """สร้าง LRC signal ที่ผ่าน channel price validation แล้ว - ให้ AI คำนวณ SL/TP และ Confidence"""
        direction = channel_result['direction']
        current_price = channel_result['current_price']
        
        # กำหนด entry และ pattern type
        entry_level = current_price
        pattern_type = "LRC_BREAKOUT_UP" if direction == 'LONG' else "LRC_BREAKOUT_DOWN"
        
        # ส่งข้อมูลให้ AI คำนวณ stop loss, take profit และ confidence ที่เหมาะสม
        # ใช้ค่า 0 เป็น placeholder สำหรับ AI
        stop_loss = 0.0  # AI จะคำนวณให้
        take_profit = 0.0  # AI จะคำนวณให้
        confidence = 0.0  # AI จะวิเคราะห์และกำหนดให้
        
        return LRCResult(
            pattern_type=pattern_type,
            confidence=confidence,  # AI จะวิเคราะห์
            signal=direction,
            strength=8.0,
            entry_level=entry_level,
            stop_loss=stop_loss,  # AI จะคำนวณ
            take_profit=take_profit,  # AI จะคำนวณ
            volume_confirm=True,
            pattern_status="FRESH_BREAKOUT",
            description=f"lrc_breakout_{direction.lower()}_with_channel_validation_ai_analysis",
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
    
    # สร้างโฟลเดอร์และข้อมูลตัวอย่างถ้าไม่มี
    if not args.test_file:
        default_file = ensure_all_required_folders()
        args.test_file = default_file
        print(f"📂 ใช้ไฟล์ข้อมูลเริ่มต้น: {default_file}")
    
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
        print("📂 Auto-creating minimal folder structure...")
        ensure_all_required_folders()
        create_sample_log_structure()
        create_readme_files()
        print("📋 Use --test-file to test with specific OHLCV data")
        print("📋 Minimal folders and config files have been created!")
        print("🚫 History, logs, and reports are disabled for maximum performance!")


if __name__ == "__main__":
    # ตรวจสอบและสร้างโครงสร้างโฟลเดอร์แบบมินิมอล
    print("🔧 ตรวจสอบและสร้างโครงสร้างโฟลเดอร์มินิมอล...")
    ensure_all_required_folders()
    create_sample_log_structure()
    create_readme_files()
    print("✅ ระบบพร้อมใช้งาน - โหมดประสิทธิภาพสูง (ไม่เก็บประวัติ)!")
    print("="*50)
    
    main()
