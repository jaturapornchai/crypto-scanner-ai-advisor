"""
Linear Regression Channel Detector
Based on TradingView Pine Script by LonesomeTheBlue
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging

class LinearRegressionChannelDetector:
    def __init__(self, length: int = 100, deviation: float = 2.0, lookback_candles: int = 5):
        """
        Initialize Linear Regression Channel Detector
        
        Args:
            length (int): Number of periods for Linear Regression calculation (default: 100)
            deviation (float): Deviation multiplier for channel boundaries (default: 2.0)
            lookback_candles (int): Number of candles to look back for breakout detection (default: 5)
        """
        self.length = length
        self.deviation = deviation
        self.lookback_candles = lookback_candles
        self.logger = logging.getLogger(__name__)
    
    def calculate_linear_regression_channel(self, data: List[Dict]) -> Optional[Dict]:
        """
        Calculate Linear Regression Channel based on Pine Script logic
        
        Args:
            data (List[Dict]): OHLCV data with at least 'length' candles
            
        Returns:
            Dict: Channel data with upper, lower, middle lines and slope
        """
        if len(data) < self.length:
            self.logger.warning(f"Insufficient data: {len(data)} < {self.length}")
            return None
        
        # Use only the most recent 'length' candles for calculation
        recent_data = data[-self.length:]
        closes = np.array([float(candle.get('close', 0)) for candle in recent_data])
        
        if len(closes) != self.length:
            return None
        
        # Calculate Linear Regression (Pine Script logic)
        # mid = sum(src, len) / len
        mid = np.mean(closes)
        
        # slope = linreg(src, len, 0) - linreg(src, len, 1)
        x = np.arange(self.length)
        slope, intercept = np.polyfit(x, closes, 1)
        
        # Calculate Linear Regression line values
        # intercept = mid - slope * floor(len / 2) + ((1 - (len % 2)) / 2) * slope
        lr_intercept = mid - slope * (self.length // 2) + ((1 - (self.length % 2)) / 2) * slope
        
        # endy = intercept + slope * (len - 1)
        lr_end = lr_intercept + slope * (self.length - 1)
        
        # Calculate standard deviation
        # dev = sqrt(sum(pow(src[x] - (slope * (len - x) + intercept), 2)) / len)
        deviations = []
        for i in range(self.length):
            lr_value = slope * (self.length - i) + lr_intercept
            deviation = pow(closes[i] - lr_value, 2)
            deviations.append(deviation)
        
        std_dev = np.sqrt(np.mean(deviations))
        
        # Calculate channel boundaries
        upper_channel = lr_end + std_dev * self.deviation
        lower_channel = lr_end - std_dev * self.deviation
        middle_line = lr_end
        
        return {
            'upper_channel': upper_channel,
            'lower_channel': lower_channel,
            'middle_line': middle_line,
            'slope': slope,
            'std_dev': std_dev,
            'lr_intercept': lr_intercept,
            'lr_end': lr_end
        }
    
    def detect_channel_breakout(self, data: List[Dict], symbol: str = "") -> Dict:
        """
        Detect Linear Regression Channel breakouts in the last 5 candles
        
        Args:
            data (List[Dict]): OHLCV data
            symbol (str): Trading symbol for logging
            
        Returns:
            Dict: Breakout detection results
        """
        if len(data) < self.length + self.lookback_candles:
            return {
                'breakout_detected': False,
                'reason': f'Insufficient data: {len(data)} < {self.length + self.lookback_candles}'
            }
        
        # Calculate channel for the base period
        channel = self.calculate_linear_regression_channel(data[:-self.lookback_candles])
        if not channel:
            return {
                'breakout_detected': False,
                'reason': 'Failed to calculate Linear Regression Channel'
            }
        
        # Check for breakouts in the last 5 candles
        breakouts = []
        recent_candles = data[-self.lookback_candles:]
        
        for i, candle in enumerate(recent_candles):
            close_price = float(candle.get('close', 0))
            high_price = float(candle.get('high', 0))
            low_price = float(candle.get('low', 0))
            volume = float(candle.get('volume', 0))
            
            candles_ago = self.lookback_candles - i
            
            # Check for bullish breakout (close above upper channel)
            if close_price > channel['upper_channel'] and channel['slope'] > 0:
                breakouts.append({
                    'type': 'bullish_breakout',
                    'action': 'LONG',
                    'candles_ago': candles_ago,
                    'breakout_price': close_price,
                    'channel_level': channel['upper_channel'],
                    'slope': channel['slope'],
                    'volume': volume
                })
            
            # Check for bearish breakout (close below lower channel)
            elif close_price < channel['lower_channel'] and channel['slope'] < 0:
                breakouts.append({
                    'type': 'bearish_breakout',
                    'action': 'SHORT',
                    'candles_ago': candles_ago,
                    'breakout_price': close_price,
                    'channel_level': channel['lower_channel'],
                    'slope': channel['slope'],
                    'volume': volume
                })
        
        if breakouts:
            # Return the most recent breakout
            latest_breakout = min(breakouts, key=lambda x: x['candles_ago'])
            
            return {
                'breakout_detected': True,
                'breakout_data': latest_breakout,
                'channel_data': channel,
                'symbol': symbol,
                'total_breakouts_found': len(breakouts)
            }
        
        return {
            'breakout_detected': False,
            'reason': 'No fresh channel breakouts found in last 5 candles',
            'channel_data': channel
        }
    
    def calculate_volume_spike(self, data: List[Dict], breakout_index: int) -> float:
        """
        Calculate volume spike ratio at breakout
        
        Args:
            data (List[Dict]): OHLCV data
            breakout_index (int): Index of breakout candle
            
        Returns:
            float: Volume spike ratio (current volume / average volume)
        """
        if breakout_index < 20 or breakout_index >= len(data):
            return 1.0
        
        # Calculate average volume of previous 20 candles
        avg_period = 20
        start_idx = max(0, breakout_index - avg_period)
        avg_volumes = [float(candle.get('volume', 0)) for candle in data[start_idx:breakout_index]]
        
        if not avg_volumes:
            return 1.0
        
        avg_volume = np.mean(avg_volumes)
        current_volume = float(data[breakout_index].get('volume', 0))
        
        if avg_volume == 0:
            return 1.0
        
        return current_volume / avg_volume
    
    def generate_trading_signals(self, data: List[Dict], symbol: str = "") -> Dict:
        """
        Generate trading signals based on Linear Regression Channel breakouts
        
        Args:
            data (List[Dict]): OHLCV data
            symbol (str): Trading symbol
            
        Returns:
            Dict: Trading signal with entry, stop loss, take profit
        """
        breakout_result = self.detect_channel_breakout(data, symbol)
        
        if not breakout_result['breakout_detected']:
            return {
                'action': 'HOLD',
                'reason': breakout_result['reason'],
                'confidence': 0
            }
        
        breakout_data = breakout_result['breakout_data']
        channel_data = breakout_result['channel_data']
        
        # Calculate volume spike
        breakout_candle_index = len(data) - breakout_data['candles_ago']
        volume_spike_ratio = self.calculate_volume_spike(data, breakout_candle_index)
        
        # Calculate confidence based on multiple factors
        confidence_factors = {
            'slope_strength': min(abs(channel_data['slope']) * 10000, 10),  # Normalize slope
            'volume_spike': min(volume_spike_ratio, 3),  # Cap at 3x
            'breakout_strength': abs(breakout_data['breakout_price'] - breakout_data['channel_level']) / breakout_data['channel_level'] * 100,
            'freshness': (6 - breakout_data['candles_ago']) * 2  # More recent = higher score
        }
        
        # Calculate overall confidence (0-100)
        confidence = (
            confidence_factors['slope_strength'] * 0.2 +
            confidence_factors['volume_spike'] * 0.3 +
            confidence_factors['breakout_strength'] * 0.3 +
            confidence_factors['freshness'] * 0.2
        ) * 10
        
        confidence = min(confidence, 100)
        
        # Calculate entry, stop loss, and take profit
        current_price = float(data[-1]['close'])
        channel_width = channel_data['upper_channel'] - channel_data['lower_channel']
        
        if breakout_data['action'] == 'LONG':
            entry_price = current_price
            stop_loss = channel_data['lower_channel']
            take_profit = current_price + channel_width
        else:  # SHORT
            entry_price = current_price
            stop_loss = channel_data['upper_channel']
            take_profit = current_price - channel_width
        
        return {
            'action': breakout_data['action'],
            'pattern_detected': f"Channel Breakout {breakout_data['type'].replace('_', ' ').title()}",
            'channel_direction': 'uptrend' if channel_data['slope'] > 0 else 'downtrend' if channel_data['slope'] < 0 else 'sideways',
            'slope': channel_data['slope'],
            'confidence': round(confidence, 1),
            'entry_price': round(entry_price, 8),
            'stop_loss': round(stop_loss, 8),
            'take_profit': round(take_profit, 8),
            'upper_channel': round(channel_data['upper_channel'], 8),
            'lower_channel': round(channel_data['lower_channel'], 8),
            'middle_line': round(channel_data['middle_line'], 8),
            'volume_confirmation': volume_spike_ratio >= 1.5,
            'breakout_freshness': 10 - breakout_data['candles_ago'],
            'breakout_candles_ago': breakout_data['candles_ago'],
            'volume_spike_ratio': round(volume_spike_ratio, 2),
            'analysis': f"Linear Regression Channel {breakout_data['type'].replace('_', ' ')} detected {breakout_data['candles_ago']} candles ago with {volume_spike_ratio:.1f}x volume spike. Channel slope: {channel_data['slope']:.6f}"
        }


def test_lrc_detector():
    """Test function for Linear Regression Channel Detector"""
    # Create sample data
    np.random.seed(42)
    base_price = 45000
    sample_data = []
    
    for i in range(120):
        price = base_price + np.random.normal(0, 100) + i * 10  # Uptrend with noise
        sample_data.append({
            'timestamp': 1672531200000 + i * 3600000,
            'open': price - 5,
            'high': price + 20,
            'low': price - 25,
            'close': price,
            'volume': 1000 + np.random.normal(0, 200)
        })
    
    # Add a breakout
    sample_data[-2]['close'] = sample_data[-2]['close'] + 200  # Strong breakout
    sample_data[-2]['volume'] = 2500  # High volume
    
    detector = LinearRegressionChannelDetector()
    result = detector.generate_trading_signals(sample_data, "TESTUSDT")
    
    print("Linear Regression Channel Detector Test Results:")
    print(f"Action: {result.get('action')}")
    print(f"Pattern: {result.get('pattern_detected')}")
    print(f"Confidence: {result.get('confidence')}%")
    print(f"Entry: {result.get('entry_price')}")
    print(f"Stop Loss: {result.get('stop_loss')}")
    print(f"Take Profit: {result.get('take_profit')}")
    print(f"Analysis: {result.get('analysis')}")


if __name__ == "__main__":
    test_lrc_detector()
