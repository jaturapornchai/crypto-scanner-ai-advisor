#!/usr/bin/env python3
"""Test the specific take profit validation issue"""

# Simulate the scenario from the error message
current_price = 0.0004602
upper_channel = 0.000444  # from the log

# Current logic in the code
channel_based_tp = upper_channel * 1.02
price_based_tp = current_price * 1.02
take_profit = max(channel_based_tp, price_based_tp)

print(f"🧪 Testing Take Profit Calculation")
print(f"Current Price: {current_price:.10f}")
print(f"Upper Channel: {upper_channel:.10f}")
print(f"Channel-based TP (upper * 1.02): {channel_based_tp:.10f}")
print(f"Price-based TP (current * 1.02): {price_based_tp:.10f}")
print(f"Final Take Profit (max): {take_profit:.10f}")
print(f"")
print(f"Validation Check:")
print(f"Take Profit > Current Price? {take_profit:.10f} > {current_price:.10f} = {take_profit > current_price}")

if take_profit > current_price:
    print("✅ VALIDATION PASSED")
else:
    print("❌ VALIDATION FAILED")
