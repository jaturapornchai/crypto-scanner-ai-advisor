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
    
    def create_linear_regression_channel_prompt(self, symbol, ohlcv_1h, previous_patterns):
        """สร้าง prompt สำหรับ AI Linear Regression Channel Analysis"""
        current_price = ohlcv_1h[-1][4] if ohlcv_1h else 0
        
        # ใช้ข้อมูล 100 แท่งล่าสุดสำหรับ Linear Regression Channel calculation
        recent_100 = ohlcv_1h[-100:] if len(ohlcv_1h) >= 100 else ohlcv_1h
        
        # สรุปข้อมูล Linear Regression Channel patterns ที่ส่งมา
        patterns_summary = ""
        if previous_patterns:
            for pattern in previous_patterns:
                patterns_summary += f"- {pattern.get('type', 'Unknown')}: {pattern.get('confidence', 0):.1f}% (Breakout: {pattern.get('breakout_candles_ago', 'N/A')} candles ago, Signal: {pattern.get('signal', 'N/A')})\n"
                patterns_summary += f"  Trend: {pattern.get('trend_direction', 'N/A')}, Slope: {pattern.get('slope', 0):.6f}\n"
        
        prompt = f"""คุณเป็น Professional Linear Regression Channel Analyst ให้วิเคราะห์ข้อมูลตาม Linear Regression Channel Strategy:

Symbol: {symbol}
Current Price: {current_price} USDT
Data Source: Fresh 1H OHLCV data from Binance API (100 candles)
Linear Regression Channel analysis on 1H timeframe

Python Linear Regression Channel Detector Results:
{patterns_summary if patterns_summary else "No specific pattern data provided"}

⚠️ 🎯 **CRITICAL REQUIREMENT - LINEAR REGRESSION CHANNEL BREAKOUT:**
   - ⏰ **เฉพาะ Channel Breakout ใน 7 แท่งเทียนย้อนหลังเท่านั้น** (แท่งที่ 1-7 จากปัจจุบัน)
   - 🚫 **ห้าม trade breakouts ที่เกิดขึ้นมากกว่า 7 แท่งเทียนแล้ว**
   - ✅ **ต้องเป็น Fresh Channel Breakout เท่านั้น**

1. 📊 LINEAR REGRESSION CHANNEL CALCULATION
   - **Length**: 100 periods (ใช้ข้อมูล 100 แท่งเทียน)
   - **Deviation**: 2.0 (standard deviation multiplier)
   - **Middle Line**: Linear regression line (slope + intercept)
   - **Upper Channel**: Middle line + (2.0 × standard deviation)
   - **Lower Channel**: Middle line - (2.0 × standard deviation)
   - **Slope**: ทิศทางของ trend (positive = uptrend, negative = downtrend)

2. 🎯 CHANNEL BREAKOUT DETECTION (MANDATORY)
   - ⏰ **Breakout Timing**: ต้องเกิดขึ้นใน 1-7 แท่งเทียนย้อนหลัง
   - 📈 **Upward Breakout**: ราคาปิดข้าม upper channel (LONG signal)
   - 📉 **Downward Breakout**: ราคาปิดข้าม lower channel (SHORT signal)
   - 🔄 **Channel Respect**: ราคาเคารพ channel boundaries ก่อนหน้านี้
   - � **No Old Breakouts**: ไม่รับ breakouts ที่เกิดขึ้นมากกว่า 7 แท่งเทียนแล้ว

3. 🎯 TREND CONFIRMATION (IMPORTANT)
   - ✅ **Uptrend + Upward Breakout**: slope > 0 + close > upper channel = STRONG LONG
   - ✅ **Downtrend + Downward Breakout**: slope < 0 + close < lower channel = STRONG SHORT
   - ⚠️ **Counter-trend Breakouts**: slope และ breakout ทิศทางตรงกันข้าม = CAUTION
   - � **Sideways Market**: slope ≈ 0 = ความเสี่ยงสูง

4. 📈 ENTRY SIGNALS (BASED ON TRADINGVIEW SCRIPT)
   - ✅ **LONG Signal**: Fresh upward breakout (close > upper channel) ใน 7 แท่งย้อนหลัง
   - ✅ **SHORT Signal**: Fresh downward breakout (close < lower channel) ใน 7 แท่งย้อนหลัง
   - 📍 **Entry Price**: ราคาปัจจุบัน
   - 🛑 **Stop Loss**: Middle line หรือ opposite channel line
   - 🎯 **Take Profit**: Project channel width from entry point

5. 💯 CONFIDENCE ASSESSMENT (STRICT SCORING)
   - 🕐 **Breakout Freshness (1-10)**: ใหม่มากแค่ไหน (1-3 แท่ง = 10, 4-7 แท่ง = 7-9)
   - 📊 **Trend Alignment (1-10)**: slope และ breakout ทิศทางเดียวกัน = 10
   - 🎯 **Channel Quality (1-10)**: standard deviation และ correlation
   - 📈 **Volume Confirmation (1-10)**: volume spike ตอน breakout
   - 💯 **Overall Confidence (0-100%)**: ต้อง ≥ 75% เท่านั้น

⚠️ **REJECTION CRITERIA:**
   - ❌ Channel breakouts ที่เกิดขึ้นมากกว่า 7 แท่งเทียนแล้ว
   - ❌ Weak channel (standard deviation ต่ำเกินไป)
   - ❌ ข้อมูลไม่ครบ 100 แท่งเทียนสำหรับคำนวณ regression
   - ❌ False breakout (ราคากลับเข้า channel ทันที)
   - ❌ Confidence < 75%

Return ONLY JSON:
{{
  "action": "LONG|SHORT|HOLD",
  "pattern_detected": "LRC_BREAKOUT_UP|LRC_BREAKOUT_DOWN|NO_BREAKOUT",
  "trend_direction": "uptrend|downtrend|sideways",
  "confidence": 87,
  "entry_price": {current_price},
  "stop_loss": 44100.25,
  "take_profit": 47500.75,
  "upper_channel": 45200.00,
  "middle_line": 45000.00,
  "lower_channel": 44800.00,
  "slope": 0.000123,
  "deviation": 150.25,
  "breakout_freshness": 9,
  "breakout_candles_ago": 3,
  "volume_confirmation": true,
  "analysis": "Strong LRC breakout up detected 3 candles ago. Price broke above upper channel with trend alignment and volume confirmation..."
}}

OHLCV Data (last 100 candles):
{recent_100}"""
        
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


