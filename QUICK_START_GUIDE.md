# 🚀 Quick Start Guide - Linear Regression Channel Trading System

## 📋 Prerequisites

- Python 3.8 or higher
- Binance Futures account with API access
- DeepSeek AI API key
- Basic understanding of cryptocurrency trading

## ⚡ 5-Minute Setup

### Step 1: Clone/Create Project

```bash
mkdir lrc-trading-system
cd lrc-trading-system
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install required packages
pip install ccxt requests python-dotenv numpy pandas scipy
```

### Step 3: Create Configuration Files

**📄 .env**
```bash
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
BINANCE_TESTNET=True  # Set to False for live trading
```

**📄 config.json**
```json
{
  "trading": {
    "position_size_usdt": 100,
    "leverage": 5,
    "max_positions": 0,
    "timeframe": "1h"
  },
  "lrc": {
    "length": 100,
    "deviation": 2.0,
    "lookback": 5
  },
  "ai": {
    "min_confidence": 80,
    "min_risk_reward": 3.0
  }
}
```

### Step 4: Create Core Files

**📄 main.py** (Minimal working version)
```python
#!/usr/bin/env python3
import ccxt
import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

class SimpleTrader:
    def __init__(self):
        # Initialize exchange
        self.exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_SECRET_KEY'),
            'sandbox': os.getenv('BINANCE_TESTNET', 'True') == 'True',
            'options': {'defaultType': 'future'}
        })
        
        # Load config
        with open('config.json') as f:
            self.config = json.load(f)
    
    def get_market_data(self, symbol):
        """Get OHLCV data for analysis"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=120)
            return ohlcv
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_lrc(self, ohlcv, length=100, deviation=2.0):
        """Simple Linear Regression Channel calculation"""
        import numpy as np
        
        if len(ohlcv) < length:
            return None
        
        # Get close prices
        closes = [candle[4] for candle in ohlcv[-length:]]
        
        # Calculate linear regression
        x = np.arange(len(closes))
        y = np.array(closes)
        
        # Linear regression coefficients
        slope, intercept = np.polyfit(x, y, 1)
        regression_line = slope * x + intercept
        
        # Calculate standard deviation
        residuals = y - regression_line
        std_dev = np.std(residuals)
        
        # Calculate channels
        upper_channel = regression_line + (deviation * std_dev)
        lower_channel = regression_line - (deviation * std_dev)
        
        return {
            'regression_line': regression_line,
            'upper_channel': upper_channel,
            'lower_channel': lower_channel,
            'current_price': closes[-1],
            'slope': slope
        }
    
    def detect_breakout(self, ohlcv, lrc_data, lookback=5):
        """Detect fresh breakouts"""
        if not lrc_data:
            return None
        
        recent_candles = ohlcv[-lookback:]
        upper_channel = lrc_data['upper_channel']
        lower_channel = lrc_data['lower_channel']
        
        for i, candle in enumerate(recent_candles):
            close_price = candle[4]
            candles_ago = len(recent_candles) - i
            
            # Check for breakouts
            if close_price > upper_channel[-lookback + i]:
                return {
                    'type': 'BREAKOUT_UP',
                    'candles_ago': candles_ago,
                    'strength': (close_price - upper_channel[-lookback + i]) / close_price * 100
                }
            elif close_price < lower_channel[-lookback + i]:
                return {
                    'type': 'BREAKOUT_DOWN',
                    'candles_ago': candles_ago,
                    'strength': (lower_channel[-lookback + i] - close_price) / close_price * 100
                }
        
        return None
    
    def analyze_symbol(self, symbol):
        """Complete symbol analysis"""
        print(f"\n🔍 Analyzing {symbol}...")
        
        # Get data
        ohlcv = self.get_market_data(symbol)
        if not ohlcv:
            return None
        
        # Calculate LRC
        lrc_data = self.calculate_lrc(ohlcv)
        if not lrc_data:
            return None
        
        # Detect breakout
        breakout = self.detect_breakout(ohlcv, lrc_data)
        if not breakout:
            print(f"   ❌ No fresh breakout detected")
            return None
        
        print(f"   ✅ {breakout['type']} detected {breakout['candles_ago']} candles ago")
        print(f"   💪 Strength: {breakout['strength']:.2f}%")
        
        # Simple signal generation
        current_price = lrc_data['current_price']
        
        if breakout['type'] == 'BREAKOUT_UP':
            # Calculate LONG positions
            channel_width = lrc_data['upper_channel'][-1] - lrc_data['lower_channel'][-1]
            stop_loss = current_price - (channel_width * 0.25)
            take_profit = current_price + (channel_width * 4.0)
            
            return {
                'action': 'LONG',
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward': (take_profit - current_price) / (current_price - stop_loss)
            }
        
        elif breakout['type'] == 'BREAKOUT_DOWN':
            # Calculate SHORT positions
            channel_width = lrc_data['upper_channel'][-1] - lrc_data['lower_channel'][-1]
            stop_loss = current_price + (channel_width * 0.25)
            take_profit = current_price - (channel_width * 4.0)
            
            return {
                'action': 'SHORT',
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward': (current_price - take_profit) / (stop_loss - current_price)
            }
        
        return None
    
    def scan_markets(self):
        """Scan multiple markets for opportunities"""
        # Get available futures symbols
        markets = self.exchange.load_markets()
        usdt_futures = [symbol for symbol in markets.keys() 
                       if symbol.endswith('/USDT:USDT') and markets[symbol]['active']]
        
        # Limit to top coins for demo
        demo_symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'BNB/USDT:USDT', 
                       'ADA/USDT:USDT', 'XRP/USDT:USDT']
        
        signals = []
        
        for symbol in demo_symbols:
            try:
                signal = self.analyze_symbol(symbol)
                if signal and signal['risk_reward'] >= 3.0:
                    signals.append({
                        'symbol': symbol,
                        **signal
                    })
                    print(f"   🎯 SIGNAL: {signal['action']} | R:R = {signal['risk_reward']:.2f}:1")
                elif signal:
                    print(f"   ⚠️  Risk-Reward {signal['risk_reward']:.2f}:1 too low (need ≥3.0)")
            except Exception as e:
                print(f"   ❌ Error analyzing {symbol}: {e}")
        
        return signals
    
    def run_scanner(self):
        """Main scanner loop"""
        print("🚀 LRC Trading Scanner Started")
        print("=" * 50)
        
        try:
            # Check exchange connection
            balance = self.exchange.fetch_balance()
            print(f"💰 USDT Balance: {balance['USDT']['free']:.2f}")
            
            # Scan for opportunities
            signals = self.scan_markets()
            
            print(f"\n📊 Scan Results:")
            print("=" * 30)
            
            if signals:
                print(f"✅ Found {len(signals)} trading opportunities:")
                for signal in signals:
                    print(f"   🎯 {signal['symbol']}: {signal['action']}")
                    print(f"      Entry: {signal['entry_price']:.4f}")
                    print(f"      SL: {signal['stop_loss']:.4f}")
                    print(f"      TP: {signal['take_profit']:.4f}")
                    print(f"      R:R: {signal['risk_reward']:.2f}:1")
                    print()
            else:
                print("❌ No trading opportunities found")
                print("💡 Waiting for fresh Linear Regression Channel breakouts...")
        
        except Exception as e:
            print(f"❌ Scanner error: {e}")

if __name__ == "__main__":
    trader = SimpleTrader()
    trader.run_scanner()
```

### Step 5: Test Run

```bash
python main.py
```

## 🎯 Expected Output

```
🚀 LRC Trading Scanner Started
==================================================
💰 USDT Balance: 1000.00

🔍 Analyzing BTC/USDT:USDT...
   ✅ BREAKOUT_UP detected 2 candles ago
   💪 Strength: 1.24%
   🎯 SIGNAL: LONG | R:R = 4.50:1

🔍 Analyzing ETH/USDT:USDT...
   ❌ No fresh breakout detected

📊 Scan Results:
==============================
✅ Found 1 trading opportunities:
   🎯 BTC/USDT:USDT: LONG
      Entry: 45000.0000
      SL: 44250.0000
      TP: 48000.0000
      R:R: 4.00:1
```

## 🔧 Next Steps

1. **Add AI Integration**: Integrate DeepSeek AI for smarter analysis
2. **Add Position Management**: Implement actual order execution
3. **Add Risk Management**: Portfolio-level risk controls
4. **Add Logging**: Comprehensive logging system
5. **Add Tests**: Unit and integration tests

## 📚 File Structure

```
lrc-trading-system/
├── main.py                 # Main scanner (this file)
├── config.json            # Configuration
├── .env                   # API keys
├── requirements.txt       # Dependencies
└── logs/                  # Logs directory
```

## ⚠️ Important Notes

- **Start with testnet** - Always test with Binance testnet first
- **Paper trading** - Test strategy before using real money
- **Risk management** - Never risk more than you can afford to lose
- **Monitor performance** - Track all trades and performance

## 🆘 Troubleshooting

**Common Issues:**

1. **API Connection Error**: Check API keys and permissions
2. **Insufficient Data**: Ensure coins have enough price history
3. **No Breakouts**: Market may be ranging - wait for volatility
4. **Low Risk-Reward**: Adjust LRC parameters or wait for better setups

## 🚀 Ready to Start!

This minimal implementation gives you:
- ✅ Linear Regression Channel calculation
- ✅ Breakout detection
- ✅ Risk-reward validation
- ✅ Multi-symbol scanning
- ✅ Paper trading signals

**Perfect starting point for building your complete trading system!** 🎯
