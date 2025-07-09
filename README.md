# 🤖 Crypto Trading AI System - Linear Regression Channel Analysis Only

## 📋 ระบบเทรด Crypto อัตโนมัติด้วย AI - Linear Regression Channel Analysis

### ⚠️ กฏสำคัญของระบบ

- ❌ **ห้ามเปิด position ซ้ำในเหรียญเดียวกัน**
- ❌ **ห้ามเปิด position เพิ่ม หรือเปลี่ยนขนาด position** ถ้า position เปิดอยู่แล้ว
- ✅ **ใช้ Linear Regression Channel เท่านั้น** - ยกเลิก Chart Patterns เดิมทั้งหมด
- ✅ **Time Frame 1H เท่านั้น** - ไม่ใช้ 4H อีกต่อไป
- ✅ **เฉพาะ Channel Breakout ใน 5 แท่งเทียนย้อนหลัง** - Fresh Breakout Only

## 🎯 Linear Regression Channel Parameters

### 📊 Technical Settings
- **Length**: 100 periods (สำหรับการคำนวณ Linear Regression)
- **Deviation**: 2.0 (สำหรับการกำหนด Channel Boundaries)
- **Source**: Close Price
- **Time Frame**: 1H เท่านั้น

### 📈 Signal Types
- **Channel Breakout Up** → LONG Position
- **Channel Breakout Down** → SHORT Position

### ⏰ Fresh Breakout Requirement
- **🎯 เฉพาะ Breakout ใน 5 แท่งเทียนย้อนหลัง**
- **❌ ไม่รับ Breakouts ที่เก่าแล้ว**
- **📊 Volume Spike ≥ 150% ตอน Breakout**
- **💯 AI Confidence ≥ 85%**

## 🔄 Trading Workflow

### 1. ตรวจสอบ Position Management
- ดึงข้อมูล positions และ orders ที่เปิดอยู่
- ตรวจสอบจำนวน orders ต่อ position (ต้องเป็น 2)
- ยกเลิก orders ที่ไม่มี positions

### 2. Linear Regression Channel Analysis
- **Pre-filter ด้วย Python LRC Detector**
- เฉพาะเหรียญที่มี Fresh Channel Breakout จึงจะส่งให้ AI
- ใช้ข้อมูล 100 แท่งล่าสุดจาก 1H timeframe

### 3. Trade Execution
- เปิด position เฉพาะที่ AI confidence ≥ 85%
- ตั้ง leverage 10x และ margin type isolated
- Position size 10 USDT

## 📁 Main Files

- `app.py` - ไฟล์หลักของระบบ
- `pattern_detector.py` - Line Breakout + EMA7 Detection (Python)
- `enhanced_position_manager.py` - Position Management
- `ai_analyzer.py` - AI Analysis
- `exchange_client.py` - Binance Connection

## 🚀 How to Run

```bash
python app.py
```

---

**📌 หมายเหตุ: ระบบนี้ใช้เงินจริงในการเทรด และใช้ Linear Regression Channel เท่านั้น**
