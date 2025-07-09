# 🔄 Linear Regression Channel Trading Rules & Workflow

## 📋 Trading Rules (LRC Only)

### ⚠️ Strict Requirements

1. **ใช้ Linear Regression Channel เท่านั้น** - ยกเลิก Chart Patterns เดิมทั้งหมด
2. **Time Frame 1H เท่านั้น** - ไม่ใช้ 4H อีกต่อไป
3. **Fresh Breakout Only** - เฉพาะ breakout ใน 5 แท่งเทียนย้อนหลัง
4. **Volume Spike Required** - volume ≥ 150% ตอน breakout
5. **AI Confidence ≥ 85%** - เพิ่มจาก 80%
6. **Pre-filter with Python** - ตรวจสอบ breakout ด้วย Python ก่อน

## 🔄 Workflow (Updated for LRC)

### Step 1: Position Management
- Check existing positions and orders
- Cancel invalid orders
- Prepare coin list (exclude coins with positions)

### Step 2: LRC Pre-filtering
- Load 1H OHLCV data (1000 candles)
- Run Python LRC breakout detection
- Filter only coins with fresh breakouts (1-5 candles ago)

### Step 3: AI Analysis (Fresh Breakouts Only)
- Send filtered coins to AI for analysis
- AI analyzes LRC using 100 most recent candles
- Require confidence ≥ 85%

### Step 4: Trade Execution
- Open positions only for AI-confirmed breakouts
- Set leverage 10x, margin isolated
- Position size 10 USDT

## 📊 LRC Technical Parameters

- **Length**: 100 periods
- **Deviation**: 2.0
- **Source**: Close Price
- **Upper Channel**: LR Line + (2.0 * Std Dev)
- **Lower Channel**: LR Line - (2.0 * Std Dev)

## 🎯 Signal Types

- **Channel Breakout Up** → LONG Position
- **Channel Breakout Down** → SHORT Position
- **No Fresh Breakout** → HOLD (skip coin)

---

**Linear Regression Channel เท่านั้น - ไม่มี Chart Patterns เดิม**
