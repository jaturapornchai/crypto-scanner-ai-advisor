#!/usr/bin/env python3
"""
Test Risk-Reward Ratio Validation
ทดสอบการตรวจสอบอัตราส่วนกำไร:ขาดทุน
ถ้ากำไรน้อยกว่าขาดทุน ให้เป็น HOLD
"""

from ai_analyzer import AIAnalyzer
import json

def test_risk_reward_validation():
    """ทดสอบการตรวจสอบ Risk-Reward Ratio"""
    print("🧪 Testing Risk-Reward Ratio Validation")
    print("=" * 60)
    
    # สร้าง AI Analyzer
    ai_analyzer = AIAnalyzer()
    
    # Test cases
    test_cases = [
        {
            "name": "Good Risk-Reward (2:1)",
            "ai_response": {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "action": "LONG",
                            "confidence": 85,
                            "stop_loss": 45000,
                            "take_profit": 47000,
                            "entry_price": 46000,
                            "profit_potential": 1000,
                            "loss_risk": 1000,
                            "risk_reward_ratio": 1.0,
                            "analysis": "Good setup with 1:1 ratio"
                        })
                    }
                }]
            },
            "expected_action": "LONG"
        },
        {
            "name": "Bad Risk-Reward (0.5:1 - กำไรน้อยกว่าขาดทุน)",
            "ai_response": {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "action": "LONG",
                            "confidence": 85,
                            "stop_loss": 45000,
                            "take_profit": 46500,
                            "entry_price": 46000,
                            "profit_potential": 500,
                            "loss_risk": 1000,
                            "risk_reward_ratio": 0.5,
                            "analysis": "Bad setup - profit less than loss"
                        })
                    }
                }]
            },
            "expected_action": "HOLD"
        },
        {
            "name": "Excellent Risk-Reward (3:1)",
            "ai_response": {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "action": "SHORT",
                            "confidence": 90,
                            "stop_loss": 46500,
                            "take_profit": 44000,
                            "entry_price": 46000,
                            "profit_potential": 2000,
                            "loss_risk": 500,
                            "risk_reward_ratio": 4.0,
                            "analysis": "Excellent setup with 4:1 ratio"
                        })
                    }
                }]
            },
            "expected_action": "SHORT"
        },
        {
            "name": "Zero Risk-Reward (0:1 - ไม่มีกำไร)",
            "ai_response": {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "action": "LONG",
                            "confidence": 80,
                            "stop_loss": 45000,
                            "take_profit": 46000,
                            "entry_price": 46000,
                            "profit_potential": 0,
                            "loss_risk": 1000,
                            "risk_reward_ratio": 0.0,
                            "analysis": "No profit potential"
                        })
                    }
                }]
            },
            "expected_action": "HOLD"
        }
    ]
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        # Parse AI response
        result = ai_analyzer.parse_ai_response(test_case['ai_response'], [])
        
        # Display results
        print(f"Entry Price: {result.get('entry_price', 0)}")
        print(f"Stop Loss: {result.get('stop_loss', 0)}")
        print(f"Take Profit: {result.get('take_profit', 0)}")
        print(f"Profit Potential: {result.get('profit_potential', 0)}")
        print(f"Loss Risk: {result.get('loss_risk', 0)}")
        print(f"Risk-Reward Ratio: {result.get('risk_reward_ratio', 0):.2f}")
        print(f"AI Decision: {result.get('action', 'UNKNOWN')}")
        print(f"Expected: {test_case['expected_action']}")
        
        # Validate result
        actual_action = result.get('action', 'UNKNOWN')
        expected_action = test_case['expected_action']
        
        if actual_action == expected_action:
            print(f"✅ PASS - Action is {actual_action} as expected")
        else:
            print(f"❌ FAIL - Expected {expected_action}, got {actual_action}")
        
        print(f"Analysis: {result.get('analysis', 'No analysis')}")

def test_manual_calculation():
    """ทดสอบการคำนวณ Risk-Reward ด้วยตนเอง"""
    print("\n" + "="*60)
    print("📊 Manual Risk-Reward Calculation Test")
    print("="*60)
    
    scenarios = [
        {
            "name": "ตัวอย่างที่ 1: กำไรมากกว่าขาดทุน (ดี)",
            "entry": 50000,
            "stop_loss": 49000,
            "take_profit": 52000,
        },
        {
            "name": "ตัวอย่างที่ 2: กำไรน้อยกว่าขาดทุน (แย่)",
            "entry": 50000,
            "stop_loss": 48000,
            "take_profit": 51000,
        },
        {
            "name": "ตัวอย่างที่ 3: กำไรเท่ากับขาดทุน (พอใช้)",
            "entry": 50000,
            "stop_loss": 49000,
            "take_profit": 51000,
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print("-" * 50)
        
        entry = scenario['entry']
        sl = scenario['stop_loss']
        tp = scenario['take_profit']
        
        profit = abs(tp - entry)
        loss = abs(entry - sl)
        ratio = profit / loss if loss > 0 else 0
        
        print(f"Entry: {entry:,.0f}")
        print(f"Stop Loss: {sl:,.0f}")
        print(f"Take Profit: {tp:,.0f}")
        print(f"Profit Potential: {profit:,.0f}")
        print(f"Loss Risk: {loss:,.0f}")
        print(f"Risk-Reward Ratio: {ratio:.2f}")
        
        if ratio >= 1.0:
            decision = "✅ TRADE (กำไร ≥ ขาดทุน)"
        else:
            decision = "❌ HOLD (กำไร < ขาดทุน)"
            
        print(f"Decision: {decision}")

if __name__ == "__main__":
    test_risk_reward_validation()
    test_manual_calculation()
    print("\n🎯 Test Complete!")
