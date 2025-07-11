"""
AI Analyzer Module - DeepSeek AI Integration for Linear Regression Channel Analysis  
โมดูลสำหรับวิเคราะห์เหรียญด้วย Linear Regression Channel Analysis แบบ Direct API (ไม่ใช้ cache)
ใช้ Python Linear Regression Channel Detector และ AI สำหรับการตัดสินใจ trading
"""

import os
import requests
import json
import subprocess
import tempfile
from dotenv import load_dotenv

class AIAnalyzer:
    """Class สำหรับวิเคราะห์เหรียญด้วย Linear Regression Channel Analysis AI - Direct API"""
    
    def __init__(self, exchange=None):
        """Initialize AI Analyzer without caching"""
        load_dotenv()
        
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = os.getenv('AI_BASE_URL', 'https://api.deepseek.com')
        
        if not self.api_key:
            raise ValueError("❌ กรุณาตั้งค่า DEEPSEEK_API_KEY ใน .env")
        
        # ไม่ใช้ Historical Data Manager เพื่อหลีกเลี่ยง caching
        self.data_manager = None
        
        print("🤖 AI Linear Regression Channel Analyzer พร้อมใช้งาน")
        print("📊 ใช้ Linear Regression Channel Detection เท่านั้น")
        print("⚡ Direct API mode - ไม่ใช้ cache")
    
    def analyze_symbol(self, symbol, ohlcv_1h, ohlcv_4h=None, previous_patterns=None):
        """วิเคราะห์เหรียญด้วย AI Linear Regression Channel Analysis - ไม่ใช้ cache"""
        try:
            if not ohlcv_1h or len(ohlcv_1h) < 100:
                return {"action": "HOLD", "confidence": 0, "stop_loss": 0, "take_profit": 0, "reason": "ข้อมูลไม่เพียงพอสำหรับ Linear Regression Channel analysis"}
            
            # ใช้ข้อมูล 1H ที่ส่งมาโดยตรง (ไม่ดึงจาก historical data manager)
            # ไม่ใช้ cache เพื่อให้ได้ข้อมูลที่อัปเดตล่าสุดเสมอ
            
            # สร้าง prompt สำหรับ AI Linear Regression Channel Analysis ใช้ข้อมูลที่ส่งมา
            prompt = self.create_linear_regression_channel_prompt(symbol, ohlcv_1h, previous_patterns)
            
            # ส่งคำขอไปยัง AI
            response = self.call_deepseek_api(prompt)
            
            # แปลงผลลัพธ์
            result = self.parse_ai_response(response, previous_patterns)
            
            # ไม่บันทึก pattern analysis เพื่อลดการใช้ storage
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            return {"action": "HOLD", "confidence": 0, "stop_loss": 0, "take_profit": 0, "reason": f"เกิดข้อผิดพลาด: {e}"}
    
    def _has_valid_patterns(self, python_patterns):
        """ตรวจสอบว่ามี pattern ที่เป็น breakout/confirmed หรือไม่"""
        if not python_patterns or not isinstance(python_patterns, list):
            return False
        
        for pattern in python_patterns:
            # ตรวจสอบว่ามี pattern ที่มี confidence สูง และเป็น breakout/confirmed
            if isinstance(pattern, dict):
                confidence = pattern.get("confidence", 0)
                pattern_status = pattern.get("pattern_status", "").upper()
                
                # เฉพาะ pattern ที่มี confidence > 60% และเป็น CONFIRMED หรือ breakout
                if confidence > 60 and pattern_status in ["CONFIRMED", "BREAKOUT"]:
                    return True
        
        return False
    
    def create_linear_regression_channel_prompt(self, symbol, ohlcv_1h, previous_patterns):
        """สร้าง prompt สำหรับ AI Linear Regression Channel Analysis - สั้นและชัดเจน"""
        current_price = ohlcv_1h[-1][4] if ohlcv_1h else 0
        
        # ใช้ข้อมูล 100 แท่งล่าสุดสำหรับ Linear Regression Channel calculation
        recent_100 = ohlcv_1h[-100:] if len(ohlcv_1h) >= 100 else ohlcv_1h
        
        # สรุปข้อมูล Linear Regression Channel patterns ที่ส่งมา
        patterns_summary = ""
        if previous_patterns:
            for pattern in previous_patterns:
                patterns_summary += f"- {pattern.get('type', 'Unknown')}: {pattern.get('signal', 'N/A')} "
                patterns_summary += f"(Trend: {pattern.get('trend_direction', 'N/A')}, Breakout: {pattern.get('breakout_candles_ago', 'N/A')} candles ago)\\n"
        
        prompt = f"""Linear Regression Channel Analysis for {symbol}

Current Price: {current_price} USDT
LRC Pattern: {patterns_summary if patterns_summary else "Analyze from OHLCV data"}

TASK: Find fresh LRC breakout within last 5 candles and calculate confidence score.

CONFIDENCE SCORING (REQUIRED):
AI must score each factor 1-10 and calculate final confidence:
- Breakout Freshness: 1-2 candles=10, 3-5 candles=7-9
- Trend Alignment: breakout direction matches slope
- Channel Quality: strong boundaries, good correlation  
- Volume Confirmation: volume spike on breakout
- Price Action: strong breakout candle
- Channel Width: optimal width (not too wide/narrow)

Formula: (Sum of 6 scores ÷ 6) × 10 = Confidence %
Example: [9,8,8,7,9,8] → Average 8.17 × 10 = 82%

RISK-REWARD VALIDATION (MANDATORY):
Calculate profit potential vs loss risk:
- Profit = |Take Profit - Entry Price|
- Loss = |Entry Price - Stop Loss|  
- Risk-Reward Ratio = Profit ÷ Loss

**RULE: If Profit ≤ Loss (Risk-Reward ≤ 1.0), then action = "HOLD"**
Example: Entry=100, TP=102, SL=97 → Profit=2, Loss=3 → Ratio=0.67 → HOLD

RULES:
- LONG: Close > Upper Channel within 5 candles
- SHORT: Close < Lower Channel within 5 candles  
- SL: Middle line or opposite channel
- TP: Entry ± (channel width × 1.5-2.0)
- Minimum confidence: 80%
- Minimum Risk-Reward Ratio: 1.0

Return JSON:
{{
  "action": "LONG|SHORT|HOLD",
  "trend_direction": "uptrend|downtrend|sideways",
  "confidence": 85,
  "breakout_freshness_score": 9,
  "trend_alignment_score": 8,
  "channel_quality_score": 8,
  "volume_confirmation_score": 7,
  "price_action_strength_score": 9,
  "channel_width_quality_score": 8,
  "stop_loss": 44100.25,
  "take_profit": 47500.75,
  "entry_price": 45000.0,
  "profit_potential": 2500.75,
  "loss_risk": 899.75,
  "risk_reward_ratio": 2.78,
  "breakout_candles_ago": 2,
  "analysis": "UP breakout 2 candles ago. Scores [9,8,8,7,9,8] = 82% confidence. Risk-Reward 2.78:1 GOOD."
}}

OHLCV Data: {recent_100}"""
        
        return prompt
    
    def call_deepseek_api(self, prompt):
        """เรียก DeepSeek API"""
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 500  # เพิ่ม max_tokens เพื่อให้ AI ตอบเต็ม
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Error calling DeepSeek API: {e}")
            return None
    
    def parse_ai_response(self, response, python_patterns):
        """แปลงผลลัพธ์จาก AI สำหรับ Linear Regression Channel Analysis"""
        try:
            if not response or 'choices' not in response:
                return {"action": "HOLD", "confidence": 0, "stop_loss": 0, "take_profit": 0}
            
            content = response['choices'][0]['message']['content']
            
            # หา JSON ใน response
            if '{' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                result = json.loads(content[start:end])
                
                # ดึงค่าจาก AI response
                action = result.get('action', 'HOLD')
                confidence = result.get('confidence', 0)  # AI calculated confidence
                stop_loss = result.get('stop_loss', 0)
                take_profit = result.get('take_profit', 0)
                entry_price = result.get('entry_price', 0)
                profit_potential = result.get('profit_potential', 0)
                loss_risk = result.get('loss_risk', 0)
                risk_reward_ratio = result.get('risk_reward_ratio', 0)
                pattern_detected = result.get('pattern_detected', 'None')
                pattern_strength = result.get('pattern_strength', 0)
                pattern_target = result.get('pattern_target', 0)
                volume_confirmation = result.get('volume_confirmation', False)
                analysis = result.get('analysis', 'AI Channel Analysis')
                
                # AI Confidence Analysis Details
                breakout_freshness_score = result.get('breakout_freshness_score', 0)
                trend_alignment_score = result.get('trend_alignment_score', 0)
                channel_quality_score = result.get('channel_quality_score', 0)
                volume_confirmation_score = result.get('volume_confirmation_score', 0)
                price_action_strength_score = result.get('price_action_strength_score', 0)
                channel_width_quality_score = result.get('channel_width_quality_score', 0)
                confidence_calculation = result.get('confidence_calculation', 'AI calculated')
                
                # ตรวจสอบ Risk-Reward Ratio ก่อน (Priority #1)
                if action != "HOLD" and risk_reward_ratio >= 0 and risk_reward_ratio < 1.0:
                    print(f"    ❌ Risk-Reward Ratio {risk_reward_ratio:.2f} < 1.0 - แก้ไขเป็น HOLD")
                    print(f"    📊 Profit: {profit_potential:.2f}, Loss: {loss_risk:.2f} → กำไรน้อยกว่าขาดทุน")
                    action = "HOLD"
                    confidence = 0
                
                # ตรวจสอบ AI calculated confidence threshold (Priority #2)
                elif confidence < 75 and action != "HOLD":
                    print(f"    ⚠️  AI Calculated Confidence {confidence}% < 75% - แก้ไขเป็น HOLD")
                    print(f"    📊 AI Scoring: Fresh={breakout_freshness_score}, Trend={trend_alignment_score}, Quality={channel_quality_score}")
                    print(f"    📊 Volume={volume_confirmation_score}, Strength={price_action_strength_score}, Width={channel_width_quality_score}")
                    action = "HOLD"
                    confidence = 0
                
                # ดึง trend_direction จาก AI result
                trend_direction = result.get('trend_direction', 'unknown')
                
                return {
                    "action": action,
                    "confidence": confidence if action != "HOLD" else 0,
                    "stop_loss": stop_loss if action != "HOLD" else 0,
                    "take_profit": take_profit if action != "HOLD" else 0,
                    "entry_price": entry_price,
                    "profit_potential": profit_potential,
                    "loss_risk": loss_risk,
                    "risk_reward_ratio": risk_reward_ratio,
                    "pattern_detected": pattern_detected,
                    "pattern_strength": pattern_strength,
                    "pattern_target": pattern_target,
                    "volume_confirmation": volume_confirmation,
                    "analysis": analysis,
                    "trend_direction": trend_direction,  # เพิ่ม trend_direction
                    # AI Confidence Analysis Details
                    "ai_confidence_breakdown": {
                        "breakout_freshness_score": breakout_freshness_score,
                        "trend_alignment_score": trend_alignment_score,
                        "channel_quality_score": channel_quality_score,
                        "volume_confirmation_score": volume_confirmation_score,
                        "price_action_strength_score": price_action_strength_score,
                        "channel_width_quality_score": channel_width_quality_score,
                        "confidence_calculation": confidence_calculation
                    }
                }
            
        except Exception as e:
            print(f"❌ Error parsing AI response: {e}")
        
        return {"action": "HOLD", "confidence": 0, "stop_loss": 0, "take_profit": 0}
    
    def format_ohlcv_for_display(self, ohlcv):
        """Format OHLCV data for display"""
        if not ohlcv:
            return "No data"
        
        # Show last 5 candles
        last_candles = ohlcv[-5:]
        formatted = []
        for candle in last_candles:
            timestamp = candle[0]
            open_price = candle[1]
            high = candle[2]
            low = candle[3]
            close = candle[4]
            volume = candle[5]
            
            formatted.append(f"O:{open_price:.4f} H:{high:.4f} L:{low:.4f} C:{close:.4f} V:{volume:.0f}")
        
        return " | ".join(formatted)
