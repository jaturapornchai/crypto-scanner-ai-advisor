"""
AI Analyzer Module - DeepSeek AI Integration for Line Breakout + EMA7 Analysis  
โมดูลสำหรับวิเคราะห์เหรียญด้วย Line Breakout + EMA7 Analysis แบบ Direct API (ไม่ใช้ cache)
ใช้ Python Line Breakout + EMA7 Detector และ AI สำหรับการตัดสินใจ trading
"""

import os
import requests
import json
import subprocess
import tempfile
from dotenv import load_dotenv

class AIAnalyzer:
    """Class สำหรับวิเคราะห์เหรียญด้วย Line Breakout + EMA7 Analysis AI - Direct API"""
    
    def __init__(self, exchange=None):
        """Initialize AI Analyzer without caching"""
        load_dotenv()
        
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = os.getenv('AI_BASE_URL', 'https://api.deepseek.com')
        
        if not self.api_key:
            raise ValueError("❌ กรุณาตั้งค่า DEEPSEEK_API_KEY ใน .env")
        
        # ไม่ใช้ Historical Data Manager เพื่อหลีกเลี่ยง caching
        self.data_manager = None
        
        print("🤖 AI Line Breakout + EMA7 Analyzer พร้อมใช้งาน")
        print("📊 ใช้ Line Breakout + EMA7 Detection เท่านั้น")
        print("⚡ Direct API mode - ไม่ใช้ cache")
    
    def analyze_symbol(self, symbol, ohlcv_1h, ohlcv_4h=None, previous_patterns=None):
        """วิเคราะห์เหรียญด้วย AI Line Breakout + EMA7 Analysis - ไม่ใช้ cache"""
        try:
            if not ohlcv_1h or len(ohlcv_1h) < 20:
                return {"action": "HOLD", "confidence": 0, "stop_loss": 0, "take_profit": 0, "reason": "ข้อมูลไม่เพียงพอสำหรับ Line Breakout + EMA7 analysis"}
            
            # ใช้ข้อมูล 1H ที่ส่งมาโดยตรง (ไม่ดึงจาก historical data manager)
            # ไม่ใช้ cache เพื่อให้ได้ข้อมูลที่อัปเดตล่าสุดเสมอ
            
            # สร้าง prompt สำหรับ AI Line Breakout + EMA7 Analysis ใช้ข้อมูลที่ส่งมา
            prompt = self.create_line_breakout_ema7_prompt(symbol, ohlcv_1h, previous_patterns)
            
            # ส่งคำขอไปยัง AI
            response = self.call_deepseek_api(prompt)
            
            # แปลงผลลัพธ์
            result = self.parse_ai_response(response, previous_patterns)
            
            # ไม่บันทึก pattern analysis เพื่อลดการใช้ storage
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            return {"action": "HOLD", "confidence": 0, "stop_loss": 0, "take_profit": 0, "reason": f"เกิดข้อผิดพลาด: {e}"}
    
    def run_python_pattern_detector(self, ohlcv_data):
        """รัน Python pattern detector เพื่อให้ได้ pattern signals"""
        try:
            # แปลง OHLCV data ให้เป็น format ที่ Python สามารถอ่านได้
            formatted_data = []
            for candle in ohlcv_data:
                formatted_data.append({
                    "timestamp": int(candle[0]),
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5])
                })
            
            # สร้างไฟล์ชั่วคราวสำหรับ OHLCV data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(formatted_data, f)
                temp_file = f.name
            
            # รัน Python pattern detector
            result = subprocess.run([
                'python', 'pattern_detector.py', temp_file
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            # ลบไฟล์ชั่วคราว
            os.unlink(temp_file)
            
            if result.returncode == 0:
                try:
                    patterns = json.loads(result.stdout)
                    print(f"📈 Python Pattern Detector พบ {len(patterns)} patterns")
                    return patterns
                except json.JSONDecodeError:
                    print("⚠️ ไม่สามารถแปลงผลลัพธ์จาก Python pattern detector")
                    return []
            else:
                print(f"❌ Python Pattern Detector Error: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"❌ Error running Python pattern detector: {e}")
            return []
    
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
    
    def create_line_breakout_ema7_prompt(self, symbol, ohlcv_1h, previous_patterns):
        """สร้าง prompt สำหรับ AI Line Breakout + EMA7 Analysis"""
        current_price = ohlcv_1h[-1][4] if ohlcv_1h else 0
        
        # ใช้ข้อมูล 20 แท่งล่าสุดสำหรับ Line Breakout + EMA7 calculation
        recent_20 = ohlcv_1h[-20:] if len(ohlcv_1h) >= 20 else ohlcv_1h
        
        # สรุปข้อมูล Line Breakout + EMA7 patterns ที่ส่งมา
        patterns_summary = ""
        if previous_patterns:
            for pattern in previous_patterns:
                patterns_summary += f"- {pattern.get('pattern', 'Unknown')}: {pattern.get('confidence', 0):.1f}% (Breakout: {pattern.get('breakout_candles_ago', 'N/A')} candles ago, Signal: {pattern.get('signal', 'N/A')})\n"
        
        prompt = f"""คุณเป็น Professional Line Breakout + EMA7 Analyst ให้วิเคราะห์ข้อมูลตาม Line Breakout + EMA7 Strategy:

Symbol: {symbol}
Current Price: {current_price} USDT
Data Source: Fresh 1H OHLCV data from Binance API (20 candles)
Line Breakout + EMA7 analysis on 1H timeframe

Python Line Breakout + EMA7 Detector Results:
{patterns_summary if patterns_summary else "No specific pattern data provided"}

⚠️ 🎯 **CRITICAL REQUIREMENT - FRESH LINE BREAKOUT + EMA7 ONLY:**
   - ⏰ **เฉพาะ Line Breakout ใน 7 แท่งเทียนย้อนหลังเท่านั้น** (แท่งที่ 1-7 จากปัจจุบัน)
   - 🚫 **ห้าม trade breakouts ที่เกิดขึ้นมากกว่า 7 แท่งเทียนแล้ว**
   - ✅ **ต้องเป็น Fresh Line Breakout + EMA7 confirmation เท่านั้น**

1. 📊 LINE BREAKOUT + EMA7 CALCULATION
   - **เส้นบน (Upper Line)**: จากจุดสูงสุดใน 20 แท่งเทียนย้อนหลัง
   - **เส้นล่าง (Lower Line)**: จากจุดต่ำสุดใน 20 แท่งเทียนย้อนหลัง
   - **EMA7**: Exponential Moving Average 7 periods
   - **Line Direction**: ทิศทางโดยรวมของ upper/lower lines

2. 🎯 LINE BREAKOUT DETECTION (MANDATORY)
   - ⏰ **Breakout Timing**: ต้องเกิดขึ้นใน 1-7 แท่งเทียนย้อนหลัง
   - 📈 **Breakout Up**: แท่งเทียนสีเขียว (close > open) ทับ/ข้ามเส้นบน (Upper Line)
   - 📉 **Breakout Down**: แท่งเทียนสีแดง (close < open) ทับ/ข้ามเส้นล่าง (Lower Line)
   - 🔄 **No Old Breakouts**: ไม่รับ breakouts ที่เกิดขึ้นมากกว่า 7 แท่งเทียนแล้ว

3. 🎯 EMA7 CONFIRMATION (MANDATORY)
   - ✅ **EMA7 Touch**: 2 แท่งเทียนล่าสุด (แท่งที่ 1-2) อย่างน้อย 1 แท่งต้องทับ/ข้าม EMA7
   - 📈 **For LONG**: ราคาอย่างน้อย 1 แท่งจาก 2 แท่งล่าสุดต้องเหนือ/ทับ EMA7
   - 📉 **For SHORT**: ราคาอย่างน้อย 1 แท่งจาก 2 แท่งล่าสุดต้องใต้/ทับ EMA7

4. 📈 ENTRY SIGNALS (HIGH PRECISION)
   - ✅ **LONG Signal**: Breakout Up ใน 7 แท่งย้อนหลัง + EMA7 confirmation ใน 2 แท่งล่าสุด
   - ✅ **SHORT Signal**: Breakout Down ใน 7 แท่งย้อนหลัง + EMA7 confirmation ใน 2 แท่งล่าสุด
   - 📍 **Entry Price**: ราคาปัจจุบัน
   - 🛑 **Stop Loss**: ใต้เส้นล่าง (LONG) หรือเหนือเส้นบน (SHORT)
   - 🎯 **Take Profit**: distance between lines projected from entry

5. 💯 CONFIDENCE ASSESSMENT (STRICT SCORING)
   - 🕐 **Breakout Freshness (1-10)**: ใหม่มากแค่ไหน (1-3 แท่ง = 10, 4-7 แท่ง = 7-9)
   - 📊 **EMA7 Confirmation (1-10)**: EMA7 touch ชัดเจนแค่ไหน
   - 🎯 **Line Quality (1-10)**: ความชัดเจนของ upper/lower lines
   - 📈 **Line Direction (1-10)**: ทิศทางของ lines สอดคล้องกับ breakout
   - 💯 **Overall Confidence (0-100%)**: ต้อง ≥ 75% เท่านั้น

⚠️ **REJECTION CRITERIA:**
   - ❌ Line breakouts ที่เกิดขึ้นมากกว่า 7 แท่งเทียนแล้ว
   - ❌ ไม่มี EMA7 confirmation ใน 2 แท่งล่าสุด
   - ❌ ข้อมูลไม่ครบ 20 แท่งเทียนสำหรับคำนวณ lines และ EMA7
   - ❌ Weak breakout หรือ sideways market
   - ❌ Confidence < 75%

Return ONLY JSON:
{{
  "action": "LONG|SHORT|HOLD",
  "pattern_detected": "Line Breakout Up|Line Breakout Down|No Breakout",
  "line_direction": "uptrend|downtrend|sideways",
  "confidence": 87,
  "entry_price": {current_price},
  "stop_loss": 44100.25,
  "take_profit": 47500.75,
  "upper_line": 45200.00,
  "lower_line": 44800.00,
  "ema7": 45000.00,
  "ema7_confirmation": true,
  "breakout_freshness": 9,
  "breakout_candles_ago": 3,
  "ema7_touch_recent": "both|candle1|candle2|none",
  "analysis": "Strong Line Breakout Up detected 3 candles ago with EMA7 confirmation. Green candle broke above upper line at 45200 with recent EMA7 touch..."
}}"""
        
        return prompt
    
    def _summarize_python_patterns(self, python_patterns):
        """สรุปผลจาก Python Pattern Detector เพื่อประหยัด AI tokens"""
        if not python_patterns or not isinstance(python_patterns, list):
            return "No patterns detected"
        
        summary = []
        for pattern in python_patterns:
            if isinstance(pattern, dict):
                pattern_type = pattern.get("pattern_type", "Unknown")
                confidence = pattern.get("confidence", 0)
                signal = pattern.get("signal", "NEUTRAL")
                status = pattern.get("pattern_status", "FORMING")
                
                summary.append(f"{pattern_type}({confidence:.1f}%,{signal},{status})")
        
        return "; ".join(summary) if summary else "No valid patterns"

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
                "max_tokens": 300
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Error calling DeepSeek API: {e}")
            return None
    
    def parse_ai_response(self, response, python_patterns):
        """แปลงผลลัพธ์จาก AI สำหรับ Line Breakout + EMA7 Analysis"""
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
                confidence = result.get('confidence', 0)
                stop_loss = result.get('stop_loss', 0)
                take_profit = result.get('take_profit', 0)
                pattern_detected = result.get('pattern_detected', 'None')
                pattern_strength = result.get('pattern_strength', 0)
                entry_price = result.get('entry_price', 0)
                pattern_target = result.get('pattern_target', 0)
                volume_confirmation = result.get('volume_confirmation', False)
                analysis = result.get('analysis', 'Chart Pattern Analysis')
                
                # ตรวจสอบ confidence threshold สำหรับ Line Breakout + EMA7
                if confidence < 75 and action != "HOLD":
                    print(f"    ⚠️  Confidence {confidence}% < 75% - แก้ไขเป็น HOLD")
                    action = "HOLD"
                    confidence = 0
                
                return {
                    "action": action,
                    "confidence": confidence if action != "HOLD" else 0,
                    "stop_loss": stop_loss if action != "HOLD" else 0,
                    "take_profit": take_profit if action != "HOLD" else 0,
                    "pattern_detected": pattern_detected,
                    "pattern_strength": pattern_strength,
                    "entry_price": entry_price,
                    "pattern_target": pattern_target,
                    "volume_confirmation": volume_confirmation,
                    "analysis": analysis
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


