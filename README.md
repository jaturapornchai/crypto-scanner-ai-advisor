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
- **Concurrent scanning** of 20 popular USDT pairs
- **Real-time market sentiment** analysis (BULLISH/BEARISH/NEUTRAL)
- **Top opportunities ranking** by confidence level
- **Comprehensive signal summary** with statistics

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

**Sample Output:**
```
🔍 Multi-Symbol Breakout Scanner
================================
📊 Scanning popular USDT pairs for breakout patterns...

🚀 Scanning 20 symbols...
✅ BNBUSDT: 10 signals
✅ BTCUSDT: 4 signals  
✅ ETHUSDT: 6 signals
⚪ XRPUSDT: No signals

⏱️  Scan completed in 0.71 seconds
📊 Processed: 20/20 symbols

🎯 BREAKOUT SIGNALS SUMMARY (55 total)
==================================================

📈 COMPREHENSIVE ANALYSIS:
   🎯 Total Signals: 55
   📊 Average Confidence: 87.6%
   🔥 High Confidence (≥70%): 50 signals
   📈 Up Breakouts: 36
   📉 Down Breakouts: 0
   🔄 Successful Retests: 19

🌡️  MARKET SENTIMENT: STRONG BULLISH 🚀

🏆 TOP OPPORTUNITIES (by confidence):
1. 📈 BTCUSDT - UP_BREAKOUT (100.0% confidence)
   Price: 108466.7000 | Time: 10:00:00
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
- Price retests previously broken level and bounces
- Requires recent breakout within 5 candles
- Tolerance: 20% of channel deviation
- Base confidence: 75% + strength bonus

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
│   └── scanner/           # Multi-symbol scanner
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

### Version 2.0 (Current)
- ✅ Implemented Pine Script Linear Regression Channel
- ✅ Added comprehensive breakout detection (UP/DOWN)
- ✅ Enhanced retest analysis with recent breakout validation
- ✅ Volume confirmation for signal quality
- ✅ Multi-symbol concurrent scanner
- ✅ Market sentiment analysis
- ✅ Confidence scoring system
- ✅ Top opportunities ranking

### Key Improvements
- **Faster scanning**: Sub-second multi-symbol analysis
- **Better accuracy**: Volume and candle pattern confirmations
- **Enhanced UI**: Rich emoji-based output with clear categorization
- **Comprehensive analysis**: Detailed statistics and market sentiment

## 📈 Performance Metrics

- **Scanner Speed**: ~0.7 seconds for 20 symbols
- **API Efficiency**: Optimized calls with proper rate limiting
- **Signal Quality**: Average confidence >85% for recent market conditions
- **Coverage**: 20 most popular USDT trading pairs

---

**Happy Trading! 🚀📈**

*Remember: The best analysis tool is your own research combined with proper risk management.*
