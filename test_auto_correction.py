#!/usr/bin/env python3
"""Test the auto-correction logic for take profit validation"""

# Simulate the validation logic
def test_tp_auto_correction():
    print("🧪 Testing Take Profit Auto-Correction Logic")
    print("=" * 50)
    
    # Test case: LONG position with invalid take profit
    side = 'buy'
    price = 0.0004602
    take_profit = 0.0004528322949646495  # Invalid - lower than current price
    
    print(f"📊 Test Scenario:")
    print(f"    Side: {side}")
    print(f"    Current Price: {price:.10f}")
    print(f"    Original Take Profit: {take_profit:.10f}")
    print(f"    Valid? {take_profit > price}")
    
    # Apply auto-correction logic
    if side == 'buy':  # LONG position
        if take_profit <= price:
            print(f"⚠️ Take Profit ({take_profit}) ต้องสูงกว่าราคาปัจจุบัน ({price}) สำหรับ LONG")
            # Auto-fix: Set take profit to 3% above current price
            corrected_tp = price * 1.03
            print(f"🔧 แก้ไขอัตโนมัติ: TP = {corrected_tp:.10f} (+3% จากราคาปัจจุบัน)")
            take_profit = corrected_tp
    
    print(f"\n✅ Final Results:")
    print(f"    Final Take Profit: {take_profit:.10f}")
    print(f"    Valid? {take_profit > price}")
    print(f"    Percentage above current: {((take_profit / price) - 1) * 100:.2f}%")

if __name__ == "__main__":
    test_tp_auto_correction()
