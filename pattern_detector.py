#!/usr/bin/env python3
"""
Line Breakout + EMA7 Detector - Python Implementation
Detects Line Breakout signals with EMA7 confirmation based on new strategy.
Replaces all previous Linear Regression Channel analysis with Line Breakout + EMA7.
"""

import json
import sys
import math
import numpy as np
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
class PatternResult:
    """Pattern analysis result - Line Breakout + EMA7 only"""
    pattern_type: str
    confidence: float
    signal: str  # LONG, SHORT, NEUTRAL
    strength: float  # 1-10 scale
    entry_level: float
    stop_loss: float
    take_profit: float
    volume_confirm: bool
    pattern_status: str
    description: str
    # Line Breakout + EMA7 specific fields
    ema7_value: float = 0.0
    candle_color: str = ""
    candle_vs_ema7: str = ""
    breakout_direction: str = ""
    breakout_candles_ago: int = 999
    has_fresh_breakout: bool = False
    middle_line: float = 0.0
    lower_channel: float = 0.0
    slope: float = 0.0
    breakout_candle_index: int = 0
    # Additional fields for fresh breakout detection
    has_fresh_breakout: bool = False
    breakout_candles_ago: int = 999

@dataclass  
class LRCResult:
    """Linear Regression Channel breakout detection result"""
    pattern_type: str  # LRC_BREAKOUT_UP, LRC_BREAKOUT_DOWN
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
    breakout_candle_index: int  # Which candle (1-5) had the breakout


class LineBreakoutEMA7Detector:
    """Line Breakout + EMA7 signal detector"""
    
    def __init__(self, data: List[OHLCV]):
        self.data = data
        
    def calculate_ema7(self) -> List[float]:
        """Calculate 7-period Exponential Moving Average"""
        if len(self.data) < 7:
            return []
            
        ema_values = []
        alpha = 2 / (7 + 1)  # EMA smoothing factor
        
        # Initialize with first close price
        ema = self.data[0].close
        ema_values.append(ema)
        
        # Calculate EMA for remaining periods
        for i in range(1, len(self.data)):
            ema = alpha * self.data[i].close + (1 - alpha) * ema
            ema_values.append(ema)
            
        return ema_values
    
    def detect_line_breakout(self) -> Tuple[bool, str, int]:
        """
        Detect line breakout within last 7 candles
        - Line Breakout Up: แท่งเทียนสีเขียว ทับเส้นบน (green candle breaks resistance)
        - Line Breakout Down: แท่งเทียนสีแดง ทับเส้นล่าง (red candle breaks support)
        Returns: (has_breakout, direction, candles_ago)
        """
        if len(self.data) < 10:
            return False, "", 999
            
        # Look for breakouts in last 7 candles
        for i in range(max(0, len(self.data) - 7), len(self.data)):
            if i < 2:  # Need at least 2 previous candles for context
                continue
                
            current = self.data[i]
            prev1 = self.data[i-1]
            prev2 = self.data[i-2]
            
            # Check for Line Breakout Up: แท่งเทียนสีเขียว ทับเส้นบน
            if (current.high > prev1.high and 
                current.high > prev2.high and
                current.close > current.open):  # Green candle (close > open)
                candles_ago = len(self.data) - 1 - i
                return True, "UP", candles_ago
                
            # Check for Line Breakout Down: แท่งเทียนสีแดง ทับเส้นล่าง
            if (current.low < prev1.low and 
                current.low < prev2.low and
                current.close < current.open):  # Red candle (close < open)
                candles_ago = len(self.data) - 1 - i
                return True, "DOWN", candles_ago
                
        return False, "", 999
    
    def analyze_2_candles_ema7_cross(self, ema_values: List[float]) -> Tuple[bool, str, str]:
        """
        Analyze if any of the 2 latest candles cross EMA7
        Returns: (has_cross, cross_type, cross_details)
        """
        if not ema_values or len(self.data) < 2:
            return False, "", ""
            
        # Get 2 latest candles and EMA7 values
        candle1 = self.data[-1]  # Latest candle
        candle2 = self.data[-2]  # Previous candle
        ema7_1 = ema_values[-1]  # Latest EMA7
        ema7_2 = ema_values[-2]  # Previous EMA7
        
        # Check if candle1 crosses EMA7
        candle1_crosses = (
            (candle1.low <= ema7_1 <= candle1.high) or  # EMA7 within candle range
            (candle1.open <= ema7_1 <= candle1.close) or  # EMA7 within body
            (candle1.close <= ema7_1 <= candle1.open)    # EMA7 within body (red candle)
        )
        
        # Check if candle2 crosses EMA7
        candle2_crosses = (
            (candle2.low <= ema7_2 <= candle2.high) or  # EMA7 within candle range
            (candle2.open <= ema7_2 <= candle2.close) or  # EMA7 within body
            (candle2.close <= ema7_2 <= candle2.open)    # EMA7 within body (red candle)
        )
        
        # Determine cross details
        if candle1_crosses and candle2_crosses:
            return True, "both", "candle1_and_candle2"
        elif candle1_crosses:
            return True, "candle1", "latest_candle"
        elif candle2_crosses:
            return True, "candle2", "previous_candle"
        else:
            return False, "none", "no_cross"
    
    def check_signal_validity(self, breakout_direction: str, has_cross: bool, cross_type: str) -> Tuple[bool, str]:
        """
        Check if the combination forms a valid signal according to NEW strategy:
        - LONG: Line Breakout Up + 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7
        - SHORT: Line Breakout Down + 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7
        """
        # LONG Signal: Line Breakout Up + any of 2 latest candles cross EMA7
        if breakout_direction == "UP" and has_cross:
            return True, "LONG"
            
        # SHORT Signal: Line Breakout Down + any of 2 latest candles cross EMA7
        if breakout_direction == "DOWN" and has_cross:
            return True, "SHORT"
            
        return False, "NEUTRAL"
    
    def calculate_confidence(self, breakout_candles_ago: int, signal: str, volume_confirm: bool) -> float:
        """Calculate confidence score based on signal quality"""
        confidence = 0.0
        
        # Breakout freshness (more recent = higher score, updated for 7 timeframes)
        if breakout_candles_ago <= 2:
            confidence += 30
        elif breakout_candles_ago <= 5:
            confidence += 25
        elif breakout_candles_ago <= 7:
            confidence += 15
        else:
            confidence += 5
            
        # Valid signal
        if signal in ["LONG", "SHORT"]:
            confidence += 40
        
        # Volume confirmation
        if volume_confirm:
            confidence += 20
            
        # EMA7 cross confirmation (implicit in valid signal)
        if signal in ["LONG", "SHORT"]:
            confidence += 10
            
        return min(confidence, 100.0)
    
    def check_volume_spike(self) -> bool:
        """Check for volume spike >= 150% in recent candles"""
        if len(self.data) < 5:
            return False
            
        # Calculate average volume of last 10 candles (excluding last 2)
        volume_data = [candle.volume for candle in self.data[-12:-2]] if len(self.data) >= 12 else [candle.volume for candle in self.data[:-2]]
        
        if not volume_data:
            return False
            
        avg_volume = sum(volume_data) / len(volume_data)
        
        # Check for volume spike in last 2 candles
        for candle in self.data[-2:]:
            if candle.volume >= avg_volume * 1.5:  # 150% spike
                return True
                
        return False
    
    def detect_signal(self) -> Optional[PatternResult]:
        """Main detection method for Line Breakout + EMA7 signals"""
        if len(self.data) < 20:
            return PatternResult(
                pattern_type="INSUFFICIENT_DATA",
                confidence=0,
                signal="NEUTRAL",
                strength=0,
                entry_level=0,
                stop_loss=0,
                take_profit=0,
                volume_confirm=False,
                pattern_status="NONE",
                description="Not enough data for Line Breakout + EMA7 analysis (need 20+ candles)",
                ema7_value=0.0,
                candle_color="",
                candle_vs_ema7="",
                breakout_direction="",
                breakout_candles_ago=999,
                has_fresh_breakout=False
            )
        
        # Calculate EMA7
        ema_values = self.calculate_ema7()
        if not ema_values:
            return None
            
        # Detect line breakout
        has_breakout, breakout_direction, candles_ago = self.detect_line_breakout()
        
        if not has_breakout:
            return PatternResult(
                pattern_type="NO_LINE_BREAKOUT",
                confidence=0,
                signal="NEUTRAL",
                strength=0,
                entry_level=0,
                stop_loss=0,
                take_profit=0,
                volume_confirm=False,
                pattern_status="NO_BREAKOUT",
                description="No fresh line breakout detected in last 5 candles",
                ema7_value=ema_values[-1] if ema_values else 0.0,
                candle_color="",
                candle_vs_ema7="",
                breakout_direction="",
                breakout_candles_ago=999,
                has_fresh_breakout=False
            )
        
        # Analyze 2 latest candles EMA7 cross
        has_cross, cross_type, cross_details = self.analyze_2_candles_ema7_cross(ema_values)
        
        # Check signal validity
        is_valid_signal, signal = self.check_signal_validity(breakout_direction, has_cross, cross_type)
        
        # Check volume confirmation
        volume_confirm = self.check_volume_spike()
        
        # Calculate confidence
        confidence = self.calculate_confidence(candles_ago, signal, volume_confirm)
        
        # Calculate price levels
        current_price = self.data[-1].close
        entry_level = current_price
        
        if signal == "LONG":
            stop_loss = current_price * 0.98  # 2% below entry
            take_profit = current_price * 1.04  # 4% above entry
            pattern_type = "LINE_BREAKOUT_UP_EMA7"
        elif signal == "SHORT":
            stop_loss = current_price * 1.02  # 2% above entry
            take_profit = current_price * 0.96  # 4% below entry
            pattern_type = "LINE_BREAKOUT_DOWN_EMA7"
        else:
            stop_loss = current_price
            take_profit = current_price
            pattern_type = "NO_VALID_SIGNAL"
        
        # Determine pattern status
        if is_valid_signal and candles_ago <= 7:  # Changed from 5 to 7
            pattern_status = "FRESH_BREAKOUT"
        elif has_breakout:
            pattern_status = "INVALID_SIGNAL"
        else:
            pattern_status = "NO_BREAKOUT"
        
        # Create description
        description = f"Line Breakout {breakout_direction} detected {candles_ago} candles ago. "
        description += f"EMA7 Cross: {cross_type} ({cross_details}). "
        
        if is_valid_signal:
            description += f"Valid {signal} signal confirmed."
        else:
            description += "Signal conditions not met for entry."
        
        return PatternResult(
            pattern_type=pattern_type,
            confidence=confidence,
            signal=signal,
            strength=confidence / 10.0,  # Convert to 1-10 scale
            entry_level=entry_level,
            stop_loss=stop_loss,
            take_profit=take_profit,
            volume_confirm=volume_confirm,
            pattern_status=pattern_status,
            description=description,
            ema7_value=ema_values[-1] if ema_values else 0.0,
            candle_color="N/A",  # No longer using candle color
            candle_vs_ema7=cross_type,  # Use cross_type instead
            breakout_direction=breakout_direction,
            breakout_candles_ago=candles_ago,
            has_fresh_breakout=has_breakout and candles_ago <= 7  # Changed from 5 to 7
        )


class ChartPatternAnalyzer:
    """Chart pattern analyzer for Line Breakout + EMA7 detection"""
    
    def __init__(self, data: List[OHLCV]):
        self.data = data
        
    def analyze_patterns(self) -> List[PatternResult]:
        """Analyze Line Breakout + EMA7 patterns only"""
        detector = LineBreakoutEMA7Detector(self.data)
        result = detector.detect_signal()
        
        if result:
            return [result]
        else:
            return [PatternResult(
                pattern_type="NO_SIGNAL",
                confidence=0,
                signal="NEUTRAL",
                strength=0,
                entry_level=0,
                stop_loss=0,
                take_profit=0,
                volume_confirm=False,
                pattern_status="NONE",
                description="No Line Breakout + EMA7 signal detected",
                ema7_value=0.0,
                candle_color="",
                candle_vs_ema7="",
                breakout_direction="",
                breakout_candles_ago=999,
                has_fresh_breakout=False
            )]


class PatternDetector:
    """Main pattern detector class for Line Breakout + EMA7 strategy"""
    
    def __init__(self):
        pass
    
    def detect_patterns(self, ohlcv_data: List[Dict]) -> Dict[str, Any]:
        """
        Detect Line Breakout + EMA7 patterns from OHLCV data
        Returns detection results in JSON format
        """
        try:
            # Convert input data to OHLCV objects
            data = []
            for item in ohlcv_data:
                if isinstance(item, list) and len(item) >= 6:
                    # Handle array format [timestamp, open, high, low, close, volume]
                    data.append(OHLCV(
                        timestamp=int(item[0]),
                        open=float(item[1]),
                        high=float(item[2]),
                        low=float(item[3]),
                        close=float(item[4]),
                        volume=float(item[5])
                    ))
                elif isinstance(item, dict):
                    # Handle dict format
                    data.append(OHLCV(
                        timestamp=int(item.get('timestamp', 0)),
                        open=float(item.get('open', 0)),
                        high=float(item.get('high', 0)),
                        low=float(item.get('low', 0)),
                        close=float(item.get('close', 0)),
                        volume=float(item.get('volume', 0))
                    ))
            
            if len(data) < 20:
                return {
                    'status': 'error',
                    'message': 'Insufficient data for Line Breakout + EMA7 analysis (need 20+ candles)',
                    'pattern_detected': False,
                    'signal': 'NEUTRAL',
                    'confidence': 0
                }
            
            # Analyze patterns
            analyzer = ChartPatternAnalyzer(data)
            results = analyzer.analyze_patterns()
            
            if not results:
                return {
                    'status': 'success',
                    'message': 'No Line Breakout + EMA7 patterns detected',
                    'pattern_detected': False,
                    'signal': 'NEUTRAL',
                    'confidence': 0
                }
            
            # Get best result
            best_result = max(results, key=lambda x: x.confidence)
            
            return {
                'status': 'success',
                'pattern_detected': best_result.has_fresh_breakout,
                'pattern_type': best_result.pattern_type,
                'signal': best_result.signal,
                'confidence': best_result.confidence,
                'strength': best_result.strength,
                'entry_level': best_result.entry_level,
                'stop_loss': best_result.stop_loss,
                'take_profit': best_result.take_profit,
                'volume_confirm': best_result.volume_confirm,
                'pattern_status': best_result.pattern_status,
                'description': best_result.description,
                'ema7_value': best_result.ema7_value,
                'candle_color': best_result.candle_color,
                'candle_vs_ema7': best_result.candle_vs_ema7,
                'breakout_direction': best_result.breakout_direction,
                'breakout_candles_ago': best_result.breakout_candles_ago,
                'has_fresh_breakout': best_result.has_fresh_breakout
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error analyzing patterns: {str(e)}',
                'pattern_detected': False,
                'signal': 'NEUTRAL',
                'confidence': 0
            }


def load_ohlcv_data(filename: str) -> List[OHLCV]:
    """Load OHLCV data from JSON file"""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    return [OHLCV(
        timestamp=item['timestamp'],
        open=item['open'],
        high=item['high'],
        low=item['low'],
        close=item['close'],
        volume=item['volume']
    ) for item in data]


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Line Breakout + EMA7 Pattern Detector')
    parser.add_argument('--input', '-i', type=str, help='Input JSON file with OHLCV data')
    parser.add_argument('--symbol', '-s', type=str, default='BTCUSDT', help='Symbol name')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    if args.input:
        try:
            with open(args.input, 'r') as f:
                ohlcv_data = json.load(f)
        except Exception as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        try:
            input_data = sys.stdin.read()
            ohlcv_data = json.loads(input_data)
        except Exception as e:
            print(f"Error reading from stdin: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Create detector and analyze
    detector = PatternDetector()
    result = detector.detect_patterns(ohlcv_data)
    
    # Output result
    if args.debug:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))


if __name__ == '__main__':
    main()
