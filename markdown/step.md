# 🤖 ระบบเทรด Crypto อัตโนมัติด้วย AI - Linear Regression Channel Analysis (อัปเดต 2025)

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
- **Main File**: ไฟล์หลักอยู่ที่ `app.py`
- **Pattern Detection**: ใช้ Line Breakout + EMA7 Confirmation เท่านั้น (ไม่มี Go dependencies)

### 📊 การตั้งค่าการเทรด

- **Time Frame**: 1H เท่านั้น (สำหรับ Line Breakout + EMA7 Analysis)
- **Data Source**: ดึงจาก Binance API ใหม่ทุกครั้ง (ไม่ใช้ cache)
- **Data Amount**: ดึงเฉพาะข้อมูลที่จำเป็น (20 แท่งเทียน 1H สำหรับ EMA7 + Breakout Detection)
- **Position Size**: 20 USDT
- **Leverage**: 10x
- **Margin Type**: Isolated
- **AI Engine**: DEEPSEEK AI
- **เงินจริง**: ใช้เงินจริงทุกขั้นตอน ไม่ต้องถาม ทำงานไปเลย
- **Console**: แสดงรายละเอียดการทำงานของระบบที่ console เพื่อตรวจสอบ

## 🎯 Line Breakout + EMA7 Signals (Updated Strategy)

### 📈 Line Breakout + EMA7 Analysis

#### 🔧 **Technical Parameters**
- **EMA Period**: 7 periods (Exponential Moving Average)
- **Breakout Detection**: ใน 7 timeframe ล่าสุด
- **EMA7 Confirmation**: 2 แท่งเทียนล่าสุดทับเส้น EMA7 (แท่งใดแท่งหนึ่ง)
- **Time Frame**: 1H เท่านั้น

#### 📊 **Signal Components**
- **EMA7 Line** - เส้น Exponential Moving Average 7 periods
- **Price Action** - การเคลื่อนไหวของราคา relative to EMA7
- **2 Candle Confirmation** - 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7

### 🎯 **Signal Detection**

#### 📈 **LONG Signals (Line Breakout Up + EMA7 Cross)**
- **Line Breakout Up** - แท่งเทียนสีเขียว ทับเส้นบน ใน 7 timeframe ล่าสุด
- **EMA7 Cross** - 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7
- **Signal**: LONG entry

#### 📉 **SHORT Signals (Line Breakout Down + EMA7 Cross)**
- **Line Breakout Down** - แท่งเทียนสีแดง ทับเส้นล่าง ใน 7 timeframe ล่าสุด
- **EMA7 Cross** - 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7
- **Signal**: SHORT entry

### 📊 การวิเคราะห์ (Enhanced Accuracy)

- ใช้ **1H timeframe เท่านั้น** (7 periods สำหรับ EMA calculation)
- เฉพาะเหรียญที่มี **USDT** เป็น quote asset
- **Line Breakout + EMA7 Analysis** แทน Chart Patterns
- **🎯 เฉพาะ Line Breakout ใน 7 timeframe ล่าสุด** - ไม่สนใจ breakouts ที่เก่าแล้ว
- **🔍 EMA7 Confirmation** - ต้องมีการยืนยันด้วย 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7
- **📊 2 Candle Analysis** - วิเคราะห์ 2 แท่งเทียนล่าสุด
- **⏰ Fresh Breakout Only** - breakout ภายใน 7 timeframe ย้อนหลังเท่านั้น

## 🤖 โครงสร้าง AI Line Breakout + EMA7 Analysis

### 📥 Input Data Format (Direct API)

```text
Symbol: {symbol}
Current Price: {current_price} USDT
Data Source: Binance API Direct
Fresh Data: Just fetched

1H Timeframe Data (20 candles - fresh from API):
- OHLCV: {ohlcv_1h_fresh_20}
- Real-time Data: No cache, always current

Line Breakout + EMA7 Analysis Required
- EMA Period: 7
- Breakout Detection: Last 7 timeframes
- EMA7 Cross Analysis: 2 latest candles vs EMA7
```

### 🧠 AI Analysis Prompt (Line Breakout + EMA7 - Fresh Breakout Only)

```text
คุณเป็น Professional Line Breakout + EMA7 Analyst ให้วิเคราะห์ข้อมูลตาม Strategy ใหม่:

🔍 คุณมีข้อมูลใหม่ล่าสุด 20 แท่งเทียนสำหรับ 1H timeframe (ดึงจาก API ใหม่)

⚠️ 🎯 **CRITICAL REQUIREMENT - LINE BREAKOUT + EMA7 STRATEGY:**
   - ⏰ **เฉพาะ Line Breakout ใน 7 timeframe ล่าสุดเท่านั้น** (timeframe ที่ 1-7 จากปัจจุบัน)
   - 🚫 **ห้าม trade breakouts ที่เกิดขึ้นมากกว่า 7 timeframe แล้ว**
   - ✅ **ต้องเป็น Fresh Line Breakout + EMA7 Confirmation เท่านั้น**

1. 📊 EMA7 CALCULATION
   - **EMA Period**: 7 periods สำหรับการคำนวณ Exponential Moving Average
   - **Source**: Close Price
   - คำนวณ EMA7 สำหรับ 20 แท่งเทียนล่าสุด

2. 🎯 LINE BREAKOUT DETECTION (MANDATORY)
   - ⏰ **Breakout Timing Check** - ต้องเกิดขึ้นใน 1-7 timeframe ย้อนหลัง
   - 📈 **Line Breakout Up**: แท่งเทียนสีเขียว ทับเส้นบน ใน 7 timeframe ล่าสุด
   - 📉 **Line Breakout Down**: แท่งเทียนสีแดง ทับเส้นล่าง ใน 7 timeframe ล่าสุด
   - 🔄 **No Old Breakouts** - ไม่รับ breakouts ที่เกิดขึ้นมากกว่า 7 timeframe แล้ว

3. 📈 EMA7 CROSS CONFIRMATION (HIGH PRECISION)
   - ✅ **LONG Signal**: Line Breakout Up (แท่งเทียนสีเขียว ทับเส้นบน) + 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7
   - ✅ **SHORT Signal**: Line Breakout Down (แท่งเทียนสีแดง ทับเส้นล่าง) + 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7
   - 📍 **Entry Price** - ราคาปัจจุบัน
   - 🛑 **Stop Loss** - 2% จากราคา entry
   - 🎯 **Take Profit** - 4% จากราคา entry

4. 💯 CONFIDENCE ASSESSMENT (STRICT SCORING)
   - 🕐 **Breakout Freshness (1-10)** - ใหม่มากแค่ไหน (1-7 timeframe = 10 คะแนน)
   - 📊 **EMA7 Cross (1-10)** - 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7
   - 🎯 **Cross Quality (1-10)** - คุณภาพการทับเส้น EMA7
   - 📈 **Breakout Strength (1-10)** - ความแรงของ breakout
   - 💯 **Overall Confidence (0-100%)** - ต้อง ≥ 85% เท่านั้น

⚠️ **REJECTION CRITERIA:**
   - ❌ Line breakouts ที่เกิดขึ้นมากกว่า 7 timeframe แล้ว
   - ❌ 2 แท่งเทียนล่าสุดไม่มีแท่งใดทับเส้น EMA7
   - ❌ Cross quality ต่ำ หรือ false cross
   - ❌ Weak breakout หรือ false breakout
   - ❌ Confidence < 85%
```

### 📤 OUTPUT FORMAT (JSON เท่านั้น)

```json
{
  "action": "LONG|SHORT|HOLD",
  "pattern_detected": "Line Breakout Up + EMA7 Cross|Line Breakout Down + EMA7 Cross|No Signal",
  "ema7_direction": "uptrend|downtrend|sideways",
  "ema7_cross": "candle1|candle2|both|none",
  "confidence": 87,
  "entry_price": 45000.25,
  "stop_loss": 44100.25,
  "take_profit": 47500.75,
  "ema7_value": 45100.00,
  "candle1_vs_ema7": "above|below|cross",
  "candle2_vs_ema7": "above|below|cross",
  "breakout_freshness": 9,
  "breakout_timeframes_ago": 3,
  "analysis": "Line Breakout Up detected 3 timeframes ago with candle crossing EMA7. Perfect LONG setup with EMA7 cross confirmation..."
}
```

### ⚠️ กฎสำคัญ AI Response (Ultra Strict)

- **ตอบเป็น JSON เท่านั้น ไม่ต้องอธิบายเพิ่ม**
- **Confidence ≥ 85% เท่านั้นจึงจะเปิด Position** (เพิ่มจาก 80%)
- **🎯 Fresh Line Breakout Only** - breakout ใน 7 timeframe ย้อนหลังเท่านั้น
- **📊 EMA7 Confirmation Required** - ต้องมีการยืนยันด้วย 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7
- **🔍 Cross Quality Check** - คุณภาพการทับเส้น EMA7 ต้องชัดเจน
- **ต้องมี Line Breakout + EMA7 Signal ที่ชัดเจน ไม่ใช่การเดา**

## � ขั้นตอนการทำงานของระบบ (อัปเดต - Direct API)

### 🔄 Main Loop (ใหม่)

- **ครั้งแรก**: รัน LOOP1 ทันทีเมื่อเริ่มโปรแกรม
- **ครั้งต่อไป**: รอจนถึงนาทีแรกของชั่วโมงถัดไป (00:00, 01:00, 02:00...)
- **รัน main_loop()** ต่อเนื่องด้วย `app.py`

### LOOP1: Position และ Order Management

#### 1. แสดงสรุป Positions และ Orders ปัจจุบัน

- **📊 สรุป Positions** - แสดงจำนวน positions ปัจจุบัน และ Total PnL
- **📋 สรุป Orders** - แสดงจำนวน orders ที่เปิดอยู่ จัดกลุ่มตาม symbol
- **💰 Balance Check** - แสดง USDT balance ที่พร้อมใช้

#### 2. ตรวจสอบ Positions และ Orders

- ดึงข้อมูล positions ที่เปิดอยู่ `symbol=รหัสเหรียญของ position`
- ให้ไปค้นหา order ใช้ `symbol` ค้นหา
- **ถ้าจำนวน order ไม่เท่ากับ 2** ให้ปิด positions นั้น และปิด orders เหรียญ symbol นั้น
- ค้นหา orders ที่ไม่มี positions ถ้ามีให้ยกเลิก orders เหล่านั้น

#### 3. การเตรียมข้อมูลเหรียญ

- **COIN** = ดึงเหรียญที่มีอยู่ใน Binance Futures
- **ไม่รวมเหรียญที่มี position เปิดอยู่**
- **เอาเฉพาะเหรียญที่มี USDT เป็น quote asset**
- **สลับตำแหน่ง (สับไพ่) เพื่อให้กระจาย**

### LOOP2: Chart Pattern Analysis และเทรด

#### วน LOOP Coin ที่ได้จาก LOOP1 ทุกเหรียญ

#### 1. ตรวจสอบ Balance แทน Position Limit (อัปเดต)

- **ตรวจสอบ balance ว่าเพียงพอสำหรับ position ใหม่หรือไม่**
- **ถ้า balance < 10 USDT (position size)** ให้หยุดรอไปที่ LOOP1 ใหม่ **ในนาทีแรกของชั่วโมงถัดไป**
- **เปิด positions ไปเรื่อยๆ จนกว่าเงินจะหมด** (ไม่จำกัด 20 positions)

#### 2. กรอง Line Breakout + EMA7 (Python) + Direct API

- **ดึงข้อมูล OHLCV ใหม่ทุกครั้ง**
  - **1H Timeframe**: ดึง 20 แท่งเทียน (เพียงพอสำหรับ EMA7 + breakout detection)
  - **ดึงจาก Binance API โดยตรง** - ไม่ใช้ cache เพื่อให้ได้ข้อมูลล่าสุด
  - **ไม่บันทึกลง JSON** - ประหยัด storage และลดความซับซ้อน

- **ส่งข้อมูลให้ AI วิเคราะห์ Line Breakout + EMA7 (เฉพาะที่ Breakout แล้ว)**
  - **🎯 Pre-filter: ตรวจสอบ Line Breakout ก่อน** - ใช้ Python Line Breakout Detector กรองเฉพาะเหรียญที่มี breakout ใน 7 timeframe ย้อนหลัง
  - **⚡ ประหยัด AI Calls** - ถาม AI เฉพาะเหรียญที่ผ่านการกรอง Line Breakout แล้วเท่านั้น
  - ใช้ข้อมูล 20 แท่งล่าสุดจาก 1H data สำหรับคำนวณ EMA7
  - **ถ้า Python Line Breakout Detector ไม่พบ Fresh Line Breakout** ให้ข้ามไปเหรียญต่อไป (ไม่ถาม AI)
  - **ถ้า AI ตอบกลับว่า action = "HOLD"** ให้ข้ามไปเหรียญต่อไป

- **ไม่บันทึกผลการวิเคราะห์**
  - ลดการใช้ storage
  - เน้นการทำงานแบบ real-time

#### 3. ถ้าเหรียญมีสัญญาณ Pattern - ทำตามลำดับ

##### 3.1 ตั้งค่า Leverage และ Margin

- **ถ้าเหรียญ leverage ไม่เท่ากับ 10x** ให้ตั้ง leverage เป็น 10x
- **ถ้าเหรียญ margin type ไม่ใช่ isolated** ให้เปลี่ยนเป็น isolated

##### 3.2 วิเคราะห์ Chart Pattern ด้วย AI

- **ส่งข้อมูล OHLCV 1H และ 4H ถาม AI**
- **AI จะวิเคราะห์ Chart Patterns และให้ JSON response**
- **ตรวจสอบ confidence > 80%** ถ้าน้อยกว่าให้ข้ามไป

##### 3.3 เปิด Position

- **เปิด position ตาม action ของ AI (LONG/SHORT)**
- **ตั้ง stop loss และ take profit ตามที่ AI แนะนำ**

### 🔄 การวนซ้ำ (อัปเดต)

- **Main Loop**: ครั้งแรกรันทันที ครั้งต่อไปรอนาทีแรกของชั่วโมงถัดไป
- **LOOP1 → LOOP2 → รอชั่วโมงต่อไป → วนซ้ำ**

## 🚀 เงื่อนไขการเปิด Position (อัปเดตใหม่)

### ✅ เงื่อนไขที่ต้องผ่าน

1. **ไม่มี position เปิดอยู่แล้วในเหรียญนั้น**
2. **Balance เพียงพอ (≥ 20 USDT)** - ไม่จำกัด 20 positions แล้ว
3. **AI ตรวจพบ Line Breakout + EMA7 Signal ที่ชัดเจน (Python)**
4. **AI Confidence ≥ 75%** (ลดจาก 85%)
5. **🎯 Fresh Line Breakout Only** - breakout ใน 7 แท่งเทียนย้อนหลัง
6. **📊 Volume Spike ≥ 150%** - volume เพิ่มขึ้นตอน breakout
7. **🔍 Data Complete** - ต้องมีข้อมูล 20 แท่งเทียนเต็ม
8. **AI ให้ action = "LONG" หรือ "SHORT" (ไม่ใช่ "HOLD")**
9. **Leverage ตั้งเป็น 10x**
10. **Margin type เป็น isolated**

### 📊 ข้อมูลที่ต้องใช้ (Direct API)

- **OHLCV 20 แท่งเทียน (1H timeframe)** - ดึงจาก API ใหม่ทุกครั้ง
- **Current Price จาก OHLCV close price** - จากข้อมูลล่าสุด
- **Line Breakout + EMA7 Analysis จาก AI (Python)** - ใช้ข้อมูล 20 แท่งล่าสุด
- **Real-time Data** - ไม่ใช้ cache เพื่อความแม่นยำ

### 🚀 การประหยัด Binance API

#### **Direct API Strategy:**

1. **ดึงเฉพาะข้อมูลที่จำเป็น** - 20 แท่งเทียน 1H เท่านั้น
2. **Pre-filter ด้วย Python Line Breakout** - กรองก่อนถาม AI
3. **ไม่ใช้ storage** - ลดความซับซ้อนและเพิ่มความเร็ว
4. **Real-time Analysis** - ข้อมูลใหม่ล่าสุดเสมอ
5. **Error Handling** - จัดการ API limit และ retry mechanism

## 🎯 สรุปการทำงาน (อัปเดต 2025)

### 🔄 Flow หลัก (ใหม่)

```text
Main Loop: First time immediately → Next time wait for next hour
    ↓
LOOP1: Position Management → Coin Preparation → Shuffle
    ↓
LOOP2: Balance Check → Python Pattern Analysis → Pattern Confirmation → Trade Execution
    ↓
Back to Main Loop (Next Hour)
```

### ⏰ Timing (อัปเดต)

- **ครั้งแรก**: รันทันทีเมื่อเริ่มโปรแกรม
- **ครั้งต่อไป**: รอนาทีแรกของชั่วโมงถัดไป (00:00, 01:00, 02:00...)
- **ใช้ 1H timeframe เท่านั้น**
- **วนซ้ำตลอดไป**

### 💡 Key Points (อัปเดต)

- **ไม่ duplicate positions**
- **เปิด positions จนกว่าเงินจะหมด** (ไม่จำกัด 20 แล้ว)
- **Position Size 20 USDT per trade** (เพิ่มจาก 10 USDT)
- **Line Breakout + EMA7 เป็นตัวกรองหลัก (Pure Python)**
- **AI Confidence > 75% เท่านั้น** (ลดจาก 85%)
- **AI decision เป็น JSON เท่านั้น**
- **Real money trading**
- **Console logging สำหรับ monitoring**

### 🚀 วิธีรัน (อัปเดต)

```bash
# รันระบบหลัก (แนะนำ)
python app.py

# หรือรันไฟล์สำรอง
python main_trading.py
```

### 📊 Line Breakout + EMA7 ที่ใช้ (Python)

**Line Breakout + EMA7 Signals:**
- Line Breakout Up (แท่งเทียนสีเขียว ทับเส้นบน) + 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7 (LONG), Line Breakout Down (แท่งเทียนสีแดง ทับเส้นล่าง) + 2 แท่งเทียนล่าสุด แท่งใดแท่งหนึ่งทับเส้น EMA7 (SHORT)

**Technical Parameters:**
- EMA Period: 7, Breakout Detection: Last 7 timeframes, Source: Close Price, Timeframe: 1H only

### 📁 ไฟล์หลัก

- `app.py` - ไฟล์หลักของระบบ
- `enhanced_position_manager.py` - จัดการ positions และ main loop
- `pattern_detector.py` - ตรวจจับ Line Breakout + EMA7 Signals (Python เท่านั้น)
- `ai_analyzer.py` - AI analysis
- `exchange_client.py` - เชื่อมต่อ exchange
- `historical_data_manager.py` - จัดการข้อมูลย้อนหลัง

---

**หมายเหตุ: ระบบนี้ใช้เงินจริงในการเทรด และเปิด positions จนกว่าเงินจะหมด**

พยายามลบไฟล์ที่ไม่เกี่ยวข้องออกเสมอ และทำให้โค้ดสะอาดที่สุดเท่าที่จะทำได้
