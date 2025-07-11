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
- **Pattern Detection**: ใช้ Linear Regression Channel (LRC) เท่านั้น (ไม่มี EMA, ไม่มี Go dependencies)

### 📊 การตั้งค่าการเทรด

- **Time Frame**: 1H เท่านั้น (สำหรับ Linear Regression Channel Analysis)
- **Data Source**: ดึงจาก Binance API ใหม่ทุกครั้ง (มี cache สำหรับประหยัด API calls)
- **Data Amount**: ดึงเฉพาะข้อมูลที่จำเป็น (100 แท่งเทียน 1H สำหรับ LRC calculation)
- **Position Size**: 100 USDT
- **Leverage**: 5x
- **Margin Type**: Isolated
- **AI Engine**: DEEPSEEK AI
- **เงินจริง**: ใช้เงินจริงทุกขั้นตอน ไม่ต้องถาม ทำงานไปเลย
- **Console**: แสดงรายละเอียดการทำงานของระบบที่ console เพื่อตรวจสอบ

## 🎯 Linear Regression Channel (LRC) Strategy

### 📈 Linear Regression Channel Analysis

#### 🔧 **Technical Parameters**
- **LRC Length**: 100 periods (Linear Regression calculation)
- **LRC Deviation**: 2.0 standard deviations
- **Breakout Detection**: ใน 5 timeframe ล่าสุดเท่านั้น
- **Channel Validation**: ราคาปัจจุบันต้องมีพื้นที่เคลื่อนไหว
- **Time Frame**: 1H เท่านั้น

#### 📊 **Signal Components**
- **Upper Channel** - เส้นบน Linear Regression + 2.0σ
- **Middle Line** - เส้น Linear Regression
- **Lower Channel** - เส้นล่าง Linear Regression - 2.0σ
- **Price Action** - การเคลื่อนไหวของราคา relative to channels

### 🎯 **Signal Detection**

#### 📈 **LONG Signals (LRC Breakout Up)**
- **Channel Breakout Up** - Close > Upper Channel ใน 5 timeframe ล่าสุด
- **Price Validation** - ราคาปัจจุบัน < Upper Channel (มีพื้นที่ขึ้น)
- **Signal**: LONG entry

#### 📉 **SHORT Signals (LRC Breakout Down)**
- **Channel Breakout Down** - Close < Lower Channel ใน 5 timeframe ล่าสุด
- **Price Validation** - ราคาปัจจุบัน > Lower Channel (มีพื้นที่ลง)
- **Signal**: SHORT entry

### 📊 การวิเคราะห์ (Statistical Approach)

- ใช้ **1H timeframe เท่านั้น** (100 periods สำหรับ LRC calculation)
- เฉพาะเหรียญที่มี **USDT** เป็น quote asset
- **Linear Regression Channel Analysis** แทน Chart Patterns
- **🎯 เฉพาะ Fresh Breakout ใน 5 timeframe ล่าสุด** - ไม่สนใจ breakouts ที่เก่าแล้ว
- **🔍 Statistical Validation** - ใช้ standard deviation สำหรับ channel width
- **📊 Price Position Check** - ตรวจสอบว่าราคามีพื้นที่เคลื่อนไหวหรือไม่
- **⏰ Fresh Breakout Only** - breakout ภายใน 5 timeframe ย้อนหลังเท่านั้น

## 🤖 โครงสร้าง AI Linear Regression Channel Analysis

### 📥 Input Data Format (Cached + Real-time)

```text
Symbol: {symbol}
Current Price: {current_price} USDT
Data Source: Binance API with Smart Cache
Fresh Data: Auto-refresh when needed

1H Timeframe Data (100 candles for LRC calculation):
- OHLCV: {ohlcv_1h_100}
- Smart Cache: Historical data cached, latest data fetched real-time

Linear Regression Channel Analysis Required
- LRC Length: 100 periods
- LRC Deviation: 2.0 standard deviations
- Breakout Detection: Last 5 timeframes only
- Price Position Validation: Required
```

### 🧠 AI Analysis Prompt (Linear Regression Channel - Fresh Breakout Only)

```text
คุณเป็น Professional Linear Regression Channel Analyst ให้วิเคราะห์ข้อมูลตาม Strategy ใหม่:

🔍 คุณมีข้อมูล 100 แท่งเทียนสำหรับ 1H timeframe สำหรับคำนวณ Linear Regression Channel

⚠️ 🎯 **CRITICAL REQUIREMENT - LINEAR REGRESSION CHANNEL STRATEGY:**
   - ⏰ **เฉพาะ LRC Breakout ใน 5 timeframe ล่าสุดเท่านั้น** (timeframe ที่ 1-5 จากปัจจุบัน)
   - 🚫 **ห้าม trade breakouts ที่เกิดขึ้นมากกว่า 5 timeframe แล้ว**
   - ✅ **ต้องเป็น Fresh LRC Breakout เท่านั้น**
   - 🔍 **ต้องตรวจสอบราคาปัจจุบันมีพื้นที่เคลื่อนไหวหรือไม่**

1. 📊 LINEAR REGRESSION CHANNEL CALCULATION
   - **LRC Length**: 100 periods สำหรับการคำนวณ Linear Regression
   - **LRC Deviation**: 2.0 standard deviations
   - **Upper Channel**: Linear Regression + (2.0 × Standard Deviation)
   - **Middle Line**: Linear Regression Line
   - **Lower Channel**: Linear Regression - (2.0 × Standard Deviation)

2. 🎯 LRC BREAKOUT DETECTION (MANDATORY)
   - ⏰ **Breakout Timing Check** - ต้องเกิดขึ้นใน 1-5 timeframe ย้อนหลัง
   - 📈 **LRC Breakout Up**: Close > Upper Channel ใน 5 timeframe ล่าสุด
   - 📉 **LRC Breakout Down**: Close < Lower Channel ใน 5 timeframe ล่าสุด
   - 🔄 **No Old Breakouts** - ไม่รับ breakouts ที่เกิดขึ้นมากกว่า 5 timeframe แล้ว

3. 📈 PRICE POSITION VALIDATION (HIGH PRECISION)
   - ✅ **LONG Signal**: LRC Breakout Up + ราคาปัจจุบัน < Upper Channel (มีพื้นที่ขึ้น)
   - ✅ **SHORT Signal**: LRC Breakout Down + ราคาปัจจุบัน > Lower Channel (มีพื้นที่ลง)
   - 📍 **Entry Price** - ราคาปัจจุบัน
   - 🛑 **Stop Loss** - Middle Line ของ channel
   - 🎯 **Take Profit** - Entry ± (channel width × 1.5)

4. 💯 CONFIDENCE ASSESSMENT (6 FACTORS SCORING)
   - 🕐 **Breakout Freshness (1-10)** - 1-2 candles=10, 3-5 candles=7-9
   - 📊 **Trend Alignment (1-10)** - breakout direction matches slope
   - 🔍 **Channel Quality (1-10)** - strong boundaries, good correlation
   - 📈 **Volume Confirmation (1-10)** - volume spike on breakout
   - 💪 **Price Action Strength (1-10)** - strong breakout candle
   - � **Channel Width Quality (1-10)** - optimal width (not too wide/narrow)
   - 💯 **Final Confidence = (Sum ÷ 6) × 10** - ต้อง ≥ 80% เท่านั้น

5. 🛡️ RISK-REWARD VALIDATION (MANDATORY)
   - 💰 **Profit Potential** = |Take Profit - Entry Price|
   - 💸 **Loss Risk** = |Entry Price - Stop Loss|
   - 📊 **Risk-Reward Ratio** = Profit ÷ Loss
   - ⚠️ **If Profit ≤ Loss (Ratio ≤ 1.0) → action = "HOLD"**

⚠️ **REJECTION CRITERIA:**
   - ❌ LRC breakouts ที่เกิดขึ้นมากกว่า 5 timeframe แล้ว
   - ❌ ราคาปัจจุบันไม่มีพื้นที่เคลื่อนไหว (stuck at channel boundary)
   - ❌ Channel quality ต่ำ หรือ weak correlation
   - ❌ Weak breakout หรือ false breakout
   - ❌ Confidence < 80%
   - ❌ Risk-Reward Ratio ≤ 1.0
```

### 📤 OUTPUT FORMAT (JSON เท่านั้น)

```json
{
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
}
```

### ⚠️ กฎสำคัญ AI Response (Ultra Strict)

- **ตอบเป็น JSON เท่านั้น ไม่ต้องอธิบายเพิ่ม**
- **Confidence ≥ 80% เท่านั้นจึงจะเปิด Position**
- **🎯 Fresh LRC Breakout Only** - breakout ใน 5 timeframe ย้อนหลังเท่านั้น
- **📊 Price Position Validation Required** - ต้องมีพื้นที่เคลื่อนไหว
- **�️ Risk-Reward Validation** - Profit > Loss เท่านั้น
- **ต้องมี LRC Breakout Signal ที่ชัดเจน ไม่ใช่การเดา**

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
- **ถ้า balance < 100 USDT (position size)** ให้หยุดรอไปที่ LOOP1 ใหม่ **ในนาทีแรกของชั่วโมงถัดไป**
- **เปิด positions ไปเรื่อยๆ จนกว่าเงินจะหมด** (ไม่จำกัด positions)

#### 2. กรอง Linear Regression Channel (Python) + Smart Cache

- **ดึงข้อมูล OHLCV ผ่าน Smart Cache System**
  - **1H Timeframe**: ดึง 120 แท่งเทียน (เพียงพอสำหรับ LRC calculation)
  - **Smart Cache**: Historical data ถูก cache, ข้อมูลล่าสุดดึงจาก API
  - **Auto-refresh**: Cache จะ refresh เมื่อข้อมูลเก่าเกิน 1 ชั่วโมง
  - **Efficient API Usage**: ลด API calls แต่ยังคงความทันสมัยของข้อมูล

- **ส่งข้อมูลให้ AI วิเคราะห์ Linear Regression Channel (เฉพาะที่ Breakout แล้ว)**
  - **🎯 Pre-filter: ตรวจสอบ LRC Breakout ก่อน** - ใช้ Python LRC Detector กรองเฉพาะเหรียญที่มี breakout ใน 5 timeframe ย้อนหลัง
  - **⚡ ประหยัด AI Calls** - ถาม AI เฉพาะเหรียญที่ผ่านการกรอง LRC Breakout แล้วเท่านั้น
  - ใช้ข้อมูล 100 แท่งล่าสุดจาก 1H data สำหรับคำนวณ Linear Regression Channel
  - **ถ้า Python LRC Detector ไม่พบ Fresh LRC Breakout** ให้ข้ามไปเหรียญต่อไป (ไม่ถาม AI)
  - **ถ้า AI ตอบกลับว่า action = "HOLD"** ให้ข้ามไปเหรียญต่อไป
  - **ถ้า Risk-Reward Ratio ≤ 1.0** ให้ข้ามไปเหรียญต่อไป (กำไร ≤ ขาดทุน)

- **บันทึกผลการวิเคราะห์แบบ Smart**
  - Cache เฉพาะข้อมูล OHLCV เพื่อประหยัด API calls
  - ไม่บันทึกผลการวิเคราะห์ AI เพื่อให้ real-time decision making

#### 3. ถ้าเหรียญมีสัญญาณ Pattern - ทำตามลำดับ

##### 3.1 ตั้งค่า Leverage และ Margin

- **ถ้าเหรียญ leverage ไม่เท่ากับ 5x** ให้ตั้ง leverage เป็น 5x
- **ถ้าเหรียญ margin type ไม่ใช่ isolated** ให้เปลี่ยนเป็น isolated

##### 3.2 วิเคราะห์ Linear Regression Channel ด้วย AI

- **ส่งข้อมูล OHLCV 1H ถาม AI**
- **AI จะวิเคราะห์ LRC Patterns และให้ JSON response**
- **ตรวจสอบ confidence ≥ 80%** ถ้าน้อยกว่าให้ข้ามไป
- **ตรวจสอบ risk-reward ratio > 1.0** ถ้าไม่ผ่านให้ข้ามไป

##### 3.3 เปิด Position

- **เปิด position ตาม action ของ AI (LONG/SHORT)**
- **ตั้ง stop loss และ take profit ตามที่ AI แนะนำ**

### 🔄 การวนซ้ำ (อัปเดต)

- **Main Loop**: ครั้งแรกรันทันที ครั้งต่อไปรอนาทีแรกของชั่วโมงถัดไป
- **LOOP1 → LOOP2 → รอชั่วโมงต่อไป → วนซ้ำ**

## 🚀 เงื่อนไขการเปิด Position (อัปเดตใหม่)

### ✅ เงื่อนไขที่ต้องผ่าน

1. **ไม่มี position เปิดอยู่แล้วในเหรียญนั้น**
2. **Balance เพียงพอ (≥ 100 USDT)** - ไม่จำกัด positions แล้ว
3. **AI ตรวจพบ Linear Regression Channel Breakout ที่ชัดเจน (Python)**
4. **AI Confidence ≥ 80%**
5. **🎯 Fresh LRC Breakout Only** - breakout ใน 5 แท่งเทียนย้อนหลัง
6. **� Price Position Valid** - ราคาปัจจุบันมีพื้นที่เคลื่อนไหว
7. **🛡️ Risk-Reward Ratio > 1.0** - กำไรมากกว่าขาดทุน
8. **🔍 Data Complete** - ต้องมีข้อมูล 100 แท่งเทียนเต็ม
9. **AI ให้ action = "LONG" หรือ "SHORT" (ไม่ใช่ "HOLD")**
10. **Leverage ตั้งเป็น 5x**
11. **Margin type เป็น isolated**

### 📊 ข้อมูลที่ต้องใช้ (Smart Cache)

- **OHLCV 120 แท่งเทียน (1H timeframe)** - ผ่าน Smart Cache System
- **Current Price จาก OHLCV close price** - จากข้อมูลล่าสุด
- **Linear Regression Channel Analysis จาก AI (Python)** - ใช้ข้อมูล 100 แท่งล่าสุด
- **Smart Cache Data** - Historical data cached, latest data real-time

### 🚀 การประหยัด Binance API

#### **Smart Cache Strategy:**

1. **Cache Historical Data** - เก็บข้อมูลเก่าไว้ใน cache
2. **Real-time Latest Data** - ดึงข้อมูลล่าสุดจาก API
3. **Pre-filter ด้วย Python LRC** - กรองก่อนถาม AI
4. **Efficient Storage** - ใช้ JSON cache สำหรับ OHLCV data
5. **Auto-refresh** - Cache refresh เมื่อข้อมูลเก่าเกิน 1 ชั่วโมง
6. **Error Handling** - จัดการ API limit และ retry mechanism

## 🎯 สรุปการทำงาน (อัปเดต 2025)

### 🔄 Flow หลัก (อัปเดต)

```text
Main Loop: First time immediately → Next time wait for next hour
    ↓
LOOP0: Hourly Position & Order Check (ทุกชั่วโมง)
    ↓
LOOP1: Coin Preparation & Shuffle
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
- **Position Size 50 USDT per trade** (เพิ่มจาก 20 USDT)
- **Linear Regression Channel เป็นตัวกรองหลัก (Pure Python)**
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

### 📊 Linear Regression Channel ที่ใช้ (Python)

**Linear Regression Channel Signals:**

- Linear Regression Channel Breakout (ราคาทะลุ upper/lower band ของ LRC) + Price Position Analysis (ราคาปัจจุบันอยู่เหนือ/ใต้ regression line) สำหรับการยืนยัน trend direction

**Technical Parameters:**

- LRC Period: 100, Deviation: 2.0, Breakout Detection: Last 5 timeframes, Source: Close Price, Timeframe: 1H only

### 📁 ไฟล์หลัก

- `app.py` - ไฟล์หลักของระบบ
- `enhanced_position_manager.py` - จัดการ positions และ main loop
- `linear_regression_detector.py` - ตรวจจับ Linear Regression Channel Signals (Python เท่านั้น)
- `ai_analyzer.py` - AI analysis with risk-reward validation
- `exchange_client.py` - เชื่อมต่อ exchange
- `historical_data_manager.py` - จัดการข้อมูลย้อนหลัง

---

**หมายเหตุ: ระบบนี้ใช้เงินจริงในการเทรด และเปิด positions จนกว่าเงินจะหมด**

พยายามลบไฟล์ที่ไม่เกี่ยวข้องออกเสมอ และทำให้โค้ดสะอาดที่สุดเท่าที่จะทำได้

### 🎯 **Smart TP/SL Algorithm (Updated)**

#### 📊 **Support & Resistance Detection**

- **Lookback Period**: 50 candles (1H timeframe)
- **Pivot Detection**: 5-candle window รอบๆ จุด pivot
- **Touch Threshold**: 0.2% ความผิดพลาดในการนับ touch
- **Minimum Touches**: 2 ครั้ง เพื่อยืนยันแนวรับ-แนวต้าน
- **Relevance Range**: แนวรับ-แนวต้านต้องอยู่ภายใน 10% จากราคาปัจจุบัน

#### 🎯 **Take Profit Strategy**

- **LONG Position**:
  - **Primary**: แนวต้าน (Resistance) - 0.5% เพื่อให้โอกาส execution
  - **Fallback**: +15% จากราคา entry หากไม่มีแนวต้านที่ชัดเจน
- **SHORT Position**:
  - **Primary**: แนวรับ (Support) + 0.5% เพื่อให้โอกาส execution
  - **Fallback**: -15% จากราคา entry หากไม่มีแนวรับที่ชัดเจน

#### 🛑 **Stop Loss Strategy**

- **LONG Position**:
  - **Primary**: แนวรับ (Support) - 0.5% เพื่อป้องกัน false breakout
  - **Fallback**: -5% จากราคา entry หากไม่มีแนวรับที่ชัดเจน
- **SHORT Position**:
  - **Primary**: แนวต้าน (Resistance) + 0.5% เพื่อป้องกัน false breakout
  - **Fallback**: +5% จากราคา entry หากไม่มีแนวต้านที่ชัดเจน

#### ✅ **Validation Rules**

- TP ต้องอยู่ในทิศทางที่ถูกต้อง (LONG: TP > Entry, SHORT: TP < Entry)
- SL ต้องอยู่ในทิศทางที่ถูกต้อง (LONG: SL < Entry, SHORT: SL > Entry)
- **🚨 Risk-Reward Ratio ต้อง > 1.0 (หากไม่ใช่จะเป็น "HOLD")**
- หาก TP/SL ไม่สมเหตุสมผล จะใช้ fallback percentage
