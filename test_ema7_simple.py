#!/usr/bin/env python3
"""
Simple test to verify EMA7 calculation
"""

from linear_regression_detector import LinearRegressionChannelDetector, OHLCV

# Create simple test data
test_data = []
for i in range(20):
    price = 100 + i * 0.1  # Simple ascending price
    test_data.append(OHLCV(
        timestamp=i,
        open=price,
        high=price + 0.5,
        low=price - 0.5,
        close=price + 0.2,
        volume=1000
    ))

# Test EMA7 calculation
detector = LinearRegressionChannelDetector(test_data)
ema7_values = detector.calculate_ema7()

print('✅ EMA7 Calculation Test Results:')
print(f'📊 Total data points: {len(test_data)}')
print(f'📊 EMA7 period: {detector.ema7_period}')
print(f'📊 EMA7 values calculated: {len(ema7_values)}')
print(f'📊 First 5 EMA7 values: {[round(v, 4) for v in ema7_values[:5]]}')
print(f'📊 Last 5 EMA7 values: {[round(v, 4) for v in ema7_values[-5:]]}')

# Test the main detection method
print('\n🔍 Testing LRC + EMA7 detection method:')
try:
    result = detector.detect_breakout_with_ema7_confirmation()
    print(f'✅ Detection method working - Signal: {result.signal}, Confidence: {result.confidence}%')
except Exception as e:
    print(f'❌ Error in detection method: {e}')
