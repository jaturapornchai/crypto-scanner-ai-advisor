# Binance Futures Trading Bot - Pine Script Linear Regression Channel Analysis

🚀 **Advanced breakout detection system** using Linear Regression Channel analysis inspired by Pine Script, designed for Binance Futures trading with 1-hour timeframe analysis.

## 🎯 Key Features

### 📊 Technical Analysis (Pine Script Implementation)
- **Linear Regression Channel** calculation (100-period, 2.0 deviation multiplier)
- **Breakout Detection** - Identifies UP/DOWN breakouts with volume confirmation
- **Retest Analysis** - Detects successful retests of broken levels
- **10-Candle Lookback** - Analyzes recent 10 candles for pattern detection
- **Confidence Scoring** - Advanced confidence calculation based on strength, volume, and candle patterns

### 🔍 Multi-Symbol Scanner
- **Sequential scanning** of ALL USDT pairs (randomized order)
- **Enhanced breakout detection** with UP/DOWN breakouts and retest validation
- **Real-time market sentiment** analysis (BULLISH/BEARISH/NEUTRAL)
- **Comprehensive signal categorization** with success/failure tracking
- **Top opportunities ranking** by confidence level

### 🤖 AI Trading Advisor
- **Smart random sampling** of 20 USDT pairs for quick analysis
- **Breakout + Retest filtering** to find high-quality setups
- **AI-generated trading recommendations** (Long/Short/Hold)
- **Fibonacci-based targets** for Take Profit and Stop Loss levels
- **Risk management guidance** with position sizing recommendations

### ⚡ Performance
- **Sub-second scanning** of multiple symbols
- **Optimized API calls** with efficient data processing
- **Background processing** support

## 🛠️ Installation & Setup

### Prerequisites
- Go 1.19 or higher
- Binance Futures API access

### Environment Setup
Create `.env` file:
```env
# Binance API Configuration
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here

# Trading Environment (testnet/live)
TRADING_ENV=testnet  # or 'live' for production

# Testnet URLs (leave unchanged)
TESTNET_BASE_URL=https://testnet.binancefuture.com
TESTNET_WS_URL=wss://stream.binancefuture.com

# Live URLs (automatic)
LIVE_BASE_URL=https://fapi.binance.com
LIVE_WS_URL=wss://fstream.binance.com
```

### Install Dependencies
```bash
go mod download
```

## 🎮 Usage Commands

### 1. 💰 Balance Check
```bash
go run cmd/balance/main.go
```
Shows your Binance Futures account balance and positions.

### 2. 📋 Trading Pairs List
```bash
# Show all USDT pairs
go run cmd/pairs/main.go

# Show only popular pairs
go run cmd/pairs/main.go --popular
```

### 3. 🎯 Single Symbol Breakout Analysis
```bash
# Analyze specific symbol
go run cmd/breakout/main.go BTCUSDT
go run cmd/breakout/main.go ETHUSDT

# Auto-add USDT suffix
go run cmd/breakout/main.go BTC
go run cmd/breakout/main.go ETH
```

### 4. 🔍 Multi-Symbol Scanner (Recommended)
```bash
go run cmd/scanner/main.go
```

### 5. 🤖 AI Trading Advisor (NEW!)
```bash
go run cmd/ai-advisor/main.go
```
Analyzes 20 random USDT pairs for breakout + retest signals and provides AI-generated trading advice with Fibonacci levels.

**Sample Output:**
```
🔍 Multi-Symbol Breakout Scanner - All USDT Pairs
================================================
📊 Scanning ALL USDT pairs for breakout patterns...

🚀 Scanning 445 USDT pairs (randomized order) - Sequential Mode...
📝 Processing one symbol at a time...

📊 [1/445] Scanning ORDIUSDT... ✅ Found 11 signals
📊 [2/445] Scanning APTUSDT... ⚪ No signals
📊 [3/445] Scanning REIUSDT... ⚪ No signals
...

⏱️  Scan completed in 45.2 seconds
📊 Processed: 445/445 symbols

📋 BREAKOUT SYMBOLS SUMMARY:
==================================================

📈 UP BREAKOUT Symbols (10):
ATOMUSDT     BNBUSDT      BTCUSDT      DASHUSDT     
ETCUSDT      ETHUSDT      THETAUSDT    TRBUSDT      

� DOWN BREAKOUT Symbols (1):
COMPUSDT     

✅ RETEST SUCCESS Symbols (9):
ATOMUSDT     BNBUSDT      DASHUSDT     ETCUSDT      
KAVAUSDT     RUNEUSDT     THETAUSDT    TRBUSDT      

❌ RETEST FAILED Symbols (39):
ADAUSDT      ALGOUSDT     AVAXUSDT     BTCUSDT      
...

🏆 TOP OPPORTUNITIES (by confidence):
1. ✅ BNBUSDT - RETEST_SUCCESS (100.0% confidence)
2. ✅ TRBUSDT - RETEST_SUCCESS (99.0% confidence)
```

**AI Advisor Sample Output:**
```
🤖 AI Trading Advisor - Breakout Analysis with Fibonacci Levels
================================================================
📊 Testing 20 random USDT pairs for breakout signals...

🎯 Found 6 coins with BREAKOUT + RETEST signals

🤖 AI ANALYSIS #1: ETHUSDT
========================================
💰 SYMBOL: ETHUSDT
💵 Current Price: $2446.31
📊 Breakout Type: UP_BREAKOUT
🎯 Confidence: 67.3%

🚀 AI RECOMMENDATION: **LONG POSITION**
📈 Rationale: Bullish breakout above resistance with retest confirmation

📊 FIBONACCI TARGETS:
🎯 Take Profit 1 (38.2%): $2569.47
🎯 Take Profit 2 (61.8%): $2597.31
🎯 Take Profit 3 (100%):  $2642.37
🛑 Stop Loss (23.6%):     $2496.57

⚡ STRATEGY:
• Enter: Market or on pullback to breakout level
• Risk/Reward: 1:2 to 1:3 ratio
• Position Size: 1-2% of portfolio
```

## 📈 Technical Analysis Details

### Linear Regression Channel Parameters
- **Length**: 100 periods (configurable)
- **Deviation Multiplier**: 2.0 (configurable)
- **Timeframe**: 1 Hour (optimized for swing trading)

### Signal Types

#### 📈 UP_BREAKOUT
- Green candle closes above upper channel + minimum threshold
- Volume confirmation (10%+ increase)
- Strong candle pattern bonus (body > 70% of range)
- Confidence: Based on support strength + breakout distance

#### 📉 DOWN_BREAKOUT  
- Red candle closes below lower channel + minimum threshold
- Volume confirmation
- Strong candle pattern bonus
- Confidence: Based on resistance strength + breakout distance

#### 🔄 RETEST_SUCCESS
- Price retests previously broken level and bounces successfully
- Requires recent breakout within 5 candles
- Validates actual bounce strength (>60% of candle range)
- Base confidence: 70% + strength bonus

#### ❌ RETEST_FAILED  
- Price fails to hold at previously broken level
- Clear breakdown below/above support/resistance
- High confidence signal for trend continuation
- Fixed confidence: 80%

### Confidence Calculation
```
Confidence = (Support Strength + Breakout Distance + Volume Bonus + Candle Pattern Bonus) / 4
- Support Strength: Number of previous candles that respected the level
- Breakout Distance: Distance beyond channel relative to deviation
- Volume Bonus: 10% if volume > previous candle
- Candle Pattern Bonus: 5% if strong candle (body > 70% range)
```

## 🏗️ Project Structure

```
tread2/
├── cmd/                    # Command-line applications
│   ├── balance/           # Account balance checker
│   ├── pairs/             # Trading pairs lister  
│   ├── breakout/          # Single symbol analyzer
│   ├── scanner/           # Multi-symbol scanner
│   └── ai-advisor/        # AI trading advisor with Fibonacci levels
├── pkg/                   # Reusable packages
│   ├── trading/           # Binance API client
│   ├── analysis/          # Technical analysis engine
│   └── utils/             # Utility functions
├── internal/              # Internal packages
│   └── config.go          # Configuration management
├── tests/                 # Unit tests
├── .env                   # Environment variables
├── go.mod                 # Go module definition
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables
- `TRADING_ENV`: Set to `testnet` for testing, `live` for production
- `BINANCE_API_KEY`: Your Binance API key
- `BINANCE_SECRET_KEY`: Your Binance secret key

### Analysis Parameters (pkg/analysis/breakout.go)
```go
// Configurable parameters
Length:    100,    // Linear regression length
DevLength: 2.0,    // Deviation multiplier
```

## 🚨 Risk Disclaimer

⚠️ **This is a technical analysis tool, not investment advice.**

- Always use testnet first
- Never risk more than you can afford to lose
- Technical indicators are not 100% accurate
- Past performance doesn't guarantee future results
- Consider multiple factors before making trading decisions

## 🔐 Security Best Practices

1. **Never commit API keys** to version control
2. **Use testnet** for development and testing
3. **Limit API permissions** (read-only recommended for analysis)
4. **Monitor rate limits** to avoid API restrictions
5. **Secure your .env file** with proper permissions

## 📊 Market Sentiment Interpretation

- **STRONG BULLISH** 🚀: Up breakouts > Down breakouts × 1.5
- **BULLISH** 📈: Up breakouts > Down breakouts
- **STRONG BEARISH** 📉: Down breakouts > Up breakouts × 1.5  
- **BEARISH** 📉: Down breakouts > Up breakouts
- **NEUTRAL** ⚖️: Roughly equal breakouts

## 🎯 Best Practices

### For Analysis
1. **Combine signals** - Look for multiple confirmations
2. **Check market context** - Consider overall trend and news
3. **Use confidence levels** - Focus on signals >70% confidence
4. **Monitor volume** - Volume confirmation increases reliability
5. **Time analysis** - Run scanner during active market hours

### For Trading (If Applied)
1. **Risk management** - Always use stop losses
2. **Position sizing** - Never risk more than 1-2% per trade
3. **Multiple timeframes** - Confirm on higher timeframes
4. **Paper trading first** - Test strategies before live trading
5. **Keep records** - Track performance and learn from results

## 🚀 Recent Updates

### Version 2.2 (Current)
- ✅ **AI Trading Advisor** with Fibonacci-based targets and stop losses
- ✅ **Smart coin filtering** - Only analyzes coins with breakout + retest signals
- ✅ **Automated trading recommendations** (Long/Short/Hold decisions)
- ✅ **Risk management integration** with position sizing guidance
- ✅ **Random sampling mode** for quick 20-coin analysis
- ✅ **Enhanced Fibonacci calculations** for precise entry/exit levels

### Version 2.1 (Previous)
- ✅ **Sequential scanning** of ALL USDT pairs instead of concurrent mode
- ✅ **Enhanced retest validation** with success/failure tracking
- ✅ **Randomized scanning order** for better market coverage
- ✅ **Improved signal categorization** with clear breakout type separation
- ✅ **Detailed retest analysis** showing actual bounce/rejection strength
- ✅ **Failed retest detection** for trend continuation signals
- ✅ **Progress checkpoints** during long scanning sessions
- ✅ **Rate limiting** to avoid API restrictions

### Key Improvements from v2.1
- **AI Integration**: Automated trading advice with Fibonacci-based levels
- **Intelligent Filtering**: Focus only on high-quality breakout + retest setups  
- **Risk Management**: Built-in position sizing and risk/reward calculations
- **Quick Analysis**: 20-coin random sampling for faster decision making
- **Actionable Insights**: Clear Long/Short recommendations with precise targets

## 📈 Performance Metrics

- **Scanner Speed**: ~45 seconds for 445 USDT pairs (sequential mode)
- **API Efficiency**: Rate limited calls (100ms delay) to prevent restrictions
- **Signal Quality**: Enhanced retest validation with 80%+ confidence for failures
- **Coverage**: ALL available USDT trading pairs with randomized scanning order

---

**Happy Trading! 🚀📈**

*Remember: The best analysis tool is your own research combined with proper risk management.*
