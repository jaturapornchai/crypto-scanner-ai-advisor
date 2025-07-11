# 🤖 ระบบเทรด Crypto อัตโนมัติด้วย AI - Chart Pattern Analysis (อัปเดต)

## 📋 กฏพื้นฐานของระบบ

### ⚠️ ข้อห้าม

- ❌ **ห้ามเปิด position ซ้ำในเหรียญเดียวกัน** แต่สามารถเปิด position ในเหรียญอื่นได้
- ❌ **ห้ามเปิด position เพิ่ม หรือเปลี่ยนขนาด position** ถ้า position เปิดอยู่แล้ว

### 🧪 การทดสอบและความสะอาด

- 🧹 **พยายามลบ file ที่ไม่เกี่ยวข้องออกเสมอ**
- 🧼 **Clean code ให้สั้นที่สุดเท่าที่จะทำได้**

## ⚙️ คุณสมบัติของระบบ

### 🔧 เทคนิคและการเชื่อมต่อ

- **CCXT**: ใช้ CCXT ทั้งระบบ
- **Exchange**: เชื่อมต่อกับ Binance Futures
- **โมดูล**: แยก file โค้ดให้เป็นโมดูลย่อย
- **Main File**: ไฟล์หลักอยู่ที่ `main_trading.py`
- **Pattern Detection**: ใช้ Linear Regression Channel เท่านั้น (ไม่มี Go dependencies)

### 📊 การตั้งค่าการเทรด

- **Time Frame**: 1H เท่านั้น (สำหรับ Linear Regression Channel Analysis)
- **Historical Data**: เก็บข้อมูลมากที่สุด (1000 แท่งเทียน) ใน JSON
- **Data Storage**: `/historical_data` folder สำหรับวิเคราะห์ต่อเนื่อง
- **Position Size**: 50 USDT
- **Leverage**: 5x
- **Margin Type**: Isolated
- **AI Engine**: DEEPSEEK AI
- **เงินจริง**: ใช้เงินจริงทุกขั้นตอน ไม่ต้องถาม ทำงานไปเลย
- **Console**: แสดงรายละเอียดการทำงานของระบบที่ console เพื่อตรวจสอบ

## 🔄 ขั้นตอนการทำงานของระบบ

### LOOP1: Position และ Order Management

#### 1. ตรวจสอบ Positions และ Orders

- ดึงข้อมูล positions ที่เปิดอยู่ `symbol=รหัสเหรียญของ position`
- ให้ไปค้นหา order ใช้ `symbol` ค้นหา
- **ถ้าจำนวน order ไม่เท่ากับ 2** ให้ปิด positions นั้น และปิด orders เหรียญ symbol นั้น
- ค้นหา orders ที่ไม่มี positions ถ้ามีให้ยกเลิก orders เหล่านั้น

#### 2. การเตรียมข้อมูลเหรียญ

- **COIN** = ดึงเหรียญที่มีอยู่ใน Binance Futures
- **ไม่รวมเหรียญที่มี position เปิดอยู่**
- **เอาเฉพาะเหรียญที่มี USDT เป็น quote asset**
- **สลับตำแหน่ง (สับไพ่) เพื่อให้กระจาย**

### LOOP2: Chart Pattern Analysis และเทรด

#### วน LOOP Coin ที่ได้จาก LOOP1 ทุกเหรียญ

#### 1. ตรวจสอบ Balance แทน Position Limit

- **ตรวจสอบ balance ว่าเพียงพอสำหรับ position ใหม่หรือไม่**
- **ถ้า balance < 50 USDT (position size)** ให้หยุดรอไปที่ LOOP1 ใหม่ **ในนาทีแรกของชั่วโมงถัดไป**
- **เปิด positions ไปเรื่อยๆ จนกว่าเงินจะหมด** (ไม่จำกัด 20 positions)

#### 2. กรอง Linear Regression Channel Breakout (Python) + ระบบประหยัด API

- **ตรวจสอบ Historical Data ที่มีอยู่ก่อน**
  - เช็คไฟล์ `historical_data/symbols/{SYMBOL}_1h.json`
  - ถ้ามีข้อมูลแล้วและ update ล่าสุดไม่เกิน 1 ชั่วโมง ให้ใช้ข้อมูลเดิม
  - ถ้าไม่มีหรือข้อมูลเก่าเกิน 1 ชั่วโมง ให้ดึงข้อมูลใหม่จาก Binance API

- **ดึงข้อมูล OHLCV อย่างประหยัด**
  - **1H Timeframe**: ดึง 1000 แท่งเทียน (ประมาณ 42 วัน)
  - **บันทึกลง JSON** ทันทีหลังดึงข้อมูล
  - **Update แบบ Incremental**: เพิ่มเฉพาะแท่งเทียนใหม่ถ้ามีข้อมูลเก่าอยู่แล้ว

- **ส่งข้อมูลให้ AI วิเคราะห์ Linear Regression Channel (เฉพาะที่ Breakout แล้ว)**
  - **🎯 Pre-filter: ตรวจสอบ Channel Breakout ก่อน** - ใช้ Python LRC Detector กรองเฉพาะเหรียญที่มี breakout ใน 5 แท่งเทียนย้อนหลัง
  - **⚡ ประหยัด AI Calls** - ถาม AI เฉพาะเหรียญที่ผ่านการกรอง Channel Breakout แล้วเท่านั้น
  - ใช้ข้อมูล 100 แท่งล่าสุดจาก 1H data สำหรับคำนวณ Linear Regression Channel
  - **ถ้า Python LRC Detector ไม่พบ Fresh Channel Breakout** ให้ข้ามไปเหรียญต่อไป (ไม่ถาม AI)
  - **ถ้า AI ตอบกลับว่า action = "HOLD"** ให้ข้ามไปเหรียญต่อไป

- **บันทึกผลการวิเคราะห์**
  - เก็บ Channel Analysis ลง `historical_data/patterns/{SYMBOL}_patterns.json`
  - เก็บสถิติการวิเคราะห์ลง `historical_data/analysis/`

#### 3. ถ้าเหรียญมีสัญญาณ Channel Breakout - ทำตามลำดับ

##### 3.1 ตั้งค่า Leverage และ Margin

- **ถ้าเหรียญ leverage ไม่เท่ากับ 5x** ให้ตั้ง leverage เป็น 5x
- **ถ้าเหรียญ margin type ไม่ใช่ isolated** ให้เปลี่ยนเป็น isolated

##### 3.2 วิเคราะห์ Linear Regression Channel ด้วย AI

- **ส่งข้อมูล OHLCV 1H ถาม AI**
- **AI จะวิเคราะห์ Linear Regression Channel และให้ JSON response**
- **ตรวจสอบ confidence ≥ 85%** ถ้าน้อยกว่าให้ข้ามไป

##### 3.3 เปิด Position

- **เปิด position ตาม action ของ AI (LONG/SHORT)**
- **ตั้ง stop loss และ take profit ตามที่ AI แนะนำ**

### 🔄 การวนซ้ำ (อัปเดต)

- **LOOP1 ครั้งแรก**: รันทันทีเมื่อเริ่มโปรแกรม
- **LOOP1 ครั้งต่อไป**: รอจนถึงนาทีแรกของชั่วโมงถัดไป (00:00, 01:00, 02:00...)
- **มี main_loop()** สำหรับรันต่อเนื่อง

## 🚀 เงื่อนไขการเปิด Position (อัปเดตใหม่)

### ✅ เงื่อนไขที่ต้องผ่าน

1. **ไม่มี position เปิดอยู่แล้วในเหรียญนั้น**
2. **Balance เพียงพอ (≥ 10 USDT)** - ไม่จำกัด 20 positions
3. **AI ตรวจพบ Linear Regression Channel Breakout ที่ชัดเจน (Python)**
4. **AI Confidence ≥ 85%** (เพิ่มจาก 80%)
5. **🎯 Fresh Channel Breakout Only** - breakout ใน 5 แท่งเทียนย้อนหลัง
6. **📊 Volume Spike ≥ 150%** - volume เพิ่มขึ้นตอน breakout
7. **🔍 Channel Data Complete** - ต้องมีข้อมูล 100 แท่งเทียนเต็ม
8. **AI ให้ action = "LONG" หรือ "SHORT" (ไม่ใช่ "HOLD")**
9. **Leverage ตั้งเป็น 5x**
10. **Margin type เป็น isolated**

### 📊 Linear Regression Channel Detection (Pure Python)

- **ใช้ `linear_regression_channel.py` เท่านั้น**
- **ไม่มี Go dependencies**
- **Channel Breakouts รองรับ**: Channel Breakout Up (LONG), Channel Breakout Down (SHORT)
- **Technical Parameters**: Length=100, Deviation=2.0, Source=Close Price, Timeframe=1H
- **Fresh Breakout Only**: เฉพาะ breakout ใน 5 แท่งเทียนย้อนหลัง
- **Output JSON format** พร้อม confidence และ signals

## 🎯 สรุปการทำงาน (อัปเดต)

### 🔄 Flow หลัก

```text
Main Loop: First time immediately → Next time wait for next hour
    ↓
LOOP1: Position Management → Coin Preparation → Shuffle
    ↓
LOOP2: Balance Check → Python LRC Analysis → Channel Breakout Confirmation → Trade Execution
    ↓
Back to Main Loop (Next Hour)
```

### ⏰ Timing

- **ครั้งแรก**: รันทันทีเมื่อเริ่มโปรแกรม
- **ครั้งต่อไป**: รอนาทีแรกของชั่วโมงถัดไป
- **ใช้ 1H timeframe เท่านั้น**
- **วนซ้ำตลอดไป**

### 💡 Key Points

- **ไม่ duplicate positions**
- **เปิด positions จนกว่าเงินจะหมด** (ไม่จำกัด 20)
- **Linear Regression Channel เป็นตัวกรองหลัก (Python)**
- **AI Confidence ≥ 85% เท่านั้น**
- **AI decision เป็น JSON เท่านั้น**
- **Real money trading**
- **Console logging สำหรับ monitoring**

### 🚀 วิธีรัน

```bash
python main_trading.py
```

### 📁 ไฟล์หลัก

- `main_trading.py` - ไฟล์หลักสำหรับรันระบบ
- `enhanced_position_manager.py` - จัดการ positions และ main loop
- `pattern_detector.py` - ตรวจจับ Linear Regression Channel Breakouts (Python เท่านั้น)
- `ai_analyzer.py` - AI analysis
- `exchange_client.py` - เชื่อมต่อ exchange
- `historical_data_manager.py` - จัดการข้อมูลย้อนหลัง

---

**หมายเหตุ: ระบบนี้ใช้เงินจริงในการเทรด และเปิด positions จนกว่าเงินจะหมด**
