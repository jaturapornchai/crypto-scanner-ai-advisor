# 🎯 Linear Regression Channel Trading System - LRC Only

## 📋 ระบบเทรด Linear Regression Channel เท่านั้น

### ⚠️ การเปลี่ยนแปลงสำคัญ

- ❌ **ยกเลิก Chart Patterns เดิมทั้งหมด** (Double Top/Bottom, Bull/Bear Flag, etc.)
- ✅ **ใช้ Linear Regression Channel เท่านั้น**
- ✅ **Time Frame 1H เท่านั้น** (ไม่ใช้ 4H อีกต่อไป)
- ✅ **เฉพาะ Breakout ใน 5 แท่งเทียนย้อนหลัง**

## 🎯 Linear Regression Channel Parameters

### 📊 Technical Configuration

- **Length**: 100 periods
- **Deviation**: 2.0
- **Source**: Close Price
- **Time Frame**: 1H เท่านั้น
- **Historical Data**: 1000 แท่งเทียน (เก็บใน JSON)

### 📈 Signal Detection

#### LONG Signals (Channel Breakout Up)
- ราคา break ขึ้นไปเหนือ Upper Channel Line
- Linear Regression มี slope เป็นบวก (uptrend)
- Volume เพิ่มขึ้น ≥ 150% ตอน breakout
- Breakout เกิดขึ้นใน 1-5 แท่งเทียนย้อนหลัง

#### SHORT Signals (Channel Breakout Down)
- ราคา break ลงไปใต้ Lower Channel Line
- Linear Regression มี slope เป็นลบ (downtrend)
- Volume เพิ่มขึ้น ≥ 150% ตอน breakout
- Breakout เกิดขึ้นใน 1-5 แท่งเทียนย้อนหลัง

### ⏰ Fresh Breakout Requirement

- **🎯 เฉพาะ Breakout ใน 5 แท่งเทียนย้อนหลัง**
- **❌ ไม่รับ Breakouts ที่เก่าแล้ว (มากกว่า 5 แท่งเทียน)**
- **📊 Volume Spike ≥ 150%**
- **💯 AI Confidence ≥ 85%**
- **🔍 ข้อมูลครบ 100 แท่งเทียนสำหรับคำนวณ Channel**

## 🤖 AI Analysis Workflow

### 1. Pre-filtering (Python LRC Detector)
- ตรวจสอบ Channel Breakout ด้วย Python ก่อน
- เฉพาะเหรียญที่มี Fresh Breakout จึงส่งให้ AI
- ประหยัด AI API calls

### 2. AI Analysis (Fresh Breakout Only)
- AI วิเคราะห์เฉพาะเหรียญที่ผ่านการกรอง
- ใช้ข้อมูล 100 แท่งล่าสุดจาก 1H
- ตรวจสอบ volume และ channel quality

### 3. Trading Decision
- เปิด position เฉพาะ confidence ≥ 85%
- ตั้ง stop loss และ take profit ตาม channel width
- Leverage 5x, Margin isolated, Position size 50 USDT

## 📁 File Structure (Updated)

```
linear_regression_channel.py    # Main LRC Detection Logic
app.py                         # Main Application
enhanced_position_manager.py   # Position Management
ai_analyzer.py                # AI Analysis (LRC focused)
exchange_client.py            # Binance Connection
historical_data_manager.py    # Data Management
```

## 🔄 Trading Loop (LRC Only)

### LOOP1: Position & Order Management
- ตรวจสอบ positions และ orders
- เตรียมรายการเหรียญ (ไม่รวมที่มี position แล้ว)
- สลับลำดับเหรียญ

### LOOP2: LRC Analysis & Trading
- ตรวจสอบ balance (≥ 10 USDT)
- ดึงข้อมูล 1H OHLCV (1000 แท่งเทียน)
- **Pre-filter ด้วย Python LRC Detector**
- **เฉพาะที่มี Fresh Breakout จึงส่งให้ AI**
- เปิด position ตาม AI recommendation

## 🚀 Execution Commands

```bash
# รันระบบ LRC Trading
python app.py

# หรือ
python main_trading.py
```

## 📊 JSON Output Format (LRC)

```json
{
  "action": "LONG|SHORT|HOLD",
  "pattern_detected": "Channel Breakout Up|Channel Breakout Down|No Breakout",
  "channel_direction": "uptrend|downtrend|sideways",
  "slope": 0.0234,
  "confidence": 87,
  "entry_price": 45000.25,
  "stop_loss": 44100.25,
  "take_profit": 47500.75,
  "upper_channel": 45200.00,
  "lower_channel": 44800.00,
  "middle_line": 45000.00,
  "volume_confirmation": true,
  "breakout_freshness": 9,
  "breakout_candles_ago": 3,
  "volume_spike_ratio": 2.1
}
```

---

## 📌 หมายเหตุสำคัญ

**ระบบนี้ใช้เงินจริงในการเทรด และใช้ Linear Regression Channel เท่านั้น - ไม่มี Chart Patterns เดิมอีกต่อไป**
