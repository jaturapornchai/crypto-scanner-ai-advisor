# 📊 Complete Trading System Rules - Linear Regression Channel Only

## 🎯 System Overview

This crypto trading system uses **Linear Regression Channel analysis only** for all trading decisions. All legacy chart patterns have been removed.

## 📋 Core Rules

### ⚠️ What Changed
- ❌ **Removed**: All chart patterns (Double Top/Bottom, Bull/Bear Flag, etc.)
- ✅ **Added**: Linear Regression Channel breakout detection only
- ✅ **Time Frame**: 1H only (removed 4H)
- ✅ **Fresh Breakouts**: Only within 5 candles

### 🎯 Trading Requirements

1. **Linear Regression Channel Breakout** (Python pre-filtered)
2. **Fresh Breakout Only** (1-5 candles ago)
3. **Volume Spike ≥ 150%** at breakout
4. **AI Confidence ≥ 85%**
5. **1H Timeframe Only**
6. **100 Candles for LR Calculation**

## 📊 LRC Technical Setup

### Parameters
- **Length**: 100 periods
- **Deviation**: 2.0
- **Source**: Close price
- **Upper Channel**: LR + (2.0 × StdDev)
- **Lower Channel**: LR - (2.0 × StdDev)

### Signals
- **Breakout Up** → LONG position
- **Breakout Down** → SHORT position
- **No Fresh Breakout** → Skip coin

## 🔄 Trading Process

### Phase 1: Position Management
- Check existing positions and orders
- Validate order counts (must be 2 per position)
- Cancel orphaned orders

### Phase 2: LRC Pre-Analysis
- Load 1H OHLCV data (1000 candles)
- Calculate Linear Regression Channel
- Detect fresh breakouts (5-candle window)
- Check volume confirmation

### Phase 3: AI Analysis
- Send only pre-filtered coins to AI
- AI analyzes using 100 recent candles
- Require ≥85% confidence
- Generate trading signals

### Phase 4: Execution
- Open positions for confirmed signals
- Set 10x leverage, isolated margin
- Position size: 10 USDT
- Set stop loss and take profit

## 📁 Key Files

- `linear_regression_channel.py` - Core LRC logic
- `app.py` - Main trading application
- `pattern_detector.py` - Updated for LRC only
- `ai_analyzer.py` - LRC-focused AI analysis

## 🚀 Execution

```bash
python app.py
```

---

**Linear Regression Channel trading system - No legacy patterns**
