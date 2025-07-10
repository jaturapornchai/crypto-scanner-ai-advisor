#!/usr/bin/env python3
"""Test the LRC take profit calculation with safety checks"""

# Simulate the exact scenario from the error
current_price = 0.000460
upper_channel = 0.000444  # Lower than current price (causing the issue)
signal = "LONG"

print(f"🧪 Testing LRC Take Profit Safety Check")
print(f"=" * 50)
print(f"Current Price: {current_price:.6f}")
print(f"Upper Channel: {upper_channel:.6f}")
print(f"Signal: {signal}")
print()

# Original logic
channel_based_tp = upper_channel * 1.02
price_based_tp = current_price * 1.02
take_profit = max(channel_based_tp, price_based_tp)

print(f"📊 Take Profit Calculation:")
print(f"Channel-based TP (upper * 1.02): {channel_based_tp:.6f}")
print(f"Price-based TP (current * 1.02): {price_based_tp:.6f}")
print(f"Initial TP (max): {take_profit:.6f}")

# Safety check
if signal == "LONG":
    if take_profit <= current_price:
        take_profit = current_price * 1.03
        print(f"🔧 Safety check: Adjusted TP to {take_profit:.6f} (+3% above current)")
    else:
        print(f"✅ No safety adjustment needed")

print(f"\nFinal Take Profit: {take_profit:.6f}")
print(f"Valid for LONG? {take_profit > current_price}")
print(f"Percentage above current: {((take_profit / current_price) - 1) * 100:.2f}%")
