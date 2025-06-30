# Tread2 Go Project - Binance Futures Trading Bot

Welcome to the Tread2 Go project! This is a comprehensive Go application for cryptocurrency trading with Binance Futures API integration.

## 🚀 Features

- **Binance Futures API Integration** - Connect to Binance Futures for trading
- **Account Balance Checking** - Get real-time trading balance information
- **Testnet Support** - Safe testing environment
- **Utility Libraries** - String, Math, and Time helper functions
- **Configuration Management** - JSON-based configuration system
- **Comprehensive Testing** - Unit tests for all components

## 📁 Project Structure

```
tread2/
├── main.go                    # Main application entry point
├── go.mod                     # Go module dependencies
├── .env                       # Environment variables (API keys)
├── config.json               # Application configuration
├── cmd/                      # Command line applications
│   ├── demo/main.go          # Full demo application
│   └── balance/main.go       # Simple balance checker
├── pkg/                      # Public library code
│   ├── trading/client.go     # Binance Futures trading client
│   └── utils/utils.go        # Utility functions
├── internal/                 # Private application code
│   └── config.go            # Configuration management
├── tests/                    # Test files
│   └── main_test.go         # Unit tests
└── README.md                # This file
```

## 🔧 Prerequisites

- **Go 1.21 or higher** installed on your system
- **Binance account** with Futures trading enabled
- **API credentials** from Binance

## ⚡ Quick Start

### 1. Clone and Setup

```bash
git clone <repository>
cd tread2
go mod tidy
```

### 2. Configure API Credentials

Create a `.env` file in the project root:

```env
# Binance API Configuration
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here

# Trading Configuration
USE_TESTNET=true  # Set to false for live trading
```

### 3. Run the Application

**Full Demo Application:**
```bash
go run main.go
```

**Simple Balance Checker:**
```bash
go run cmd/balance/main.go
```

**Build and Run:**
```bash
go build -o tread2.exe
.\tread2.exe
```

## 🔑 Getting Binance API Keys

1. **Create Binance Account**: Go to [binance.com](https://binance.com) and create an account
2. **Enable Futures Trading**: Complete the Futures trading setup
3. **Create API Key**: 
   - Go to Account → API Management
   - Create new API key
   - Enable "Enable Futures" permission
   - Save your API key and secret key

### 🧪 Testnet Setup (Recommended)

For safe testing, use Binance Futures Testnet:

1. Go to [testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Login with your Binance account
3. Create testnet API credentials
4. Set `USE_TESTNET=true` in your `.env` file

## 📊 Usage Examples

### Check Account Balance

```go
package main

import (
    "context"
    "log"
    "tread2/pkg/trading"
)

func main() {
    client, err := trading.NewTradingClient()
    if err != nil {
        log.Fatal(err)
    }
    
    ctx := context.Background()
    
    // Display full account summary
    client.DisplayAccountSummary(ctx)
    
    // Get tradable balance
    balance, err := client.GetTradableBalance(ctx)
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("Available for trading: %.4f USDT\n", balance)
}
```

### Using Utility Functions

```go
package main

import (
    "fmt"
    "tread2/pkg/utils"
)

func main() {
    // String utilities
    stringHelper := utils.NewStringHelper()
    fmt.Println(stringHelper.Capitalize("hello world"))  // "Hello world"
    fmt.Println(stringHelper.Reverse("golang"))          // "gnalog"
    fmt.Println(stringHelper.IsPalindrome("racecar"))    // true
    
    // Math utilities
    mathHelper := utils.NewMathHelper()
    result, err := mathHelper.Divide(10, 3)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Result: %.2f\n", result)  // Result: 3.33
}
```

## 🧪 Testing

Run all tests:
```bash
go test ./tests/ -v
```

Run specific test:
```bash
go test ./tests/ -v -run TestStringHelper_Capitalize
```

## 🛠️ Available Commands

### Using Go commands:
```bash
# Run main application
go run main.go

# Run balance checker
go run cmd/balance/main.go

# Run demo application
go run cmd/demo/main.go

# Build application
go build -o tread2.exe

# Run tests
go test ./tests/ -v

# Install dependencies
go mod tidy

# Format code
go fmt ./...
```

### Using Makefile:
```bash
# Build the application
make build

# Run the application
make run

# Run tests
make test

# Clean build files
make clean

# Format code
make fmt

# Show help
make help
```

## 🔒 Security Best Practices

1. **Never commit API keys** to version control
2. **Use testnet** for development and testing
3. **Set IP restrictions** on your API keys
4. **Use minimal permissions** required for your use case
5. **Regularly rotate** your API keys
6. **Monitor your account** for unusual activity

## 📈 Trading Features

### Current Features:
- ✅ Account balance checking
- ✅ Futures account information
- ✅ Testnet support
- ✅ Error handling and validation

### Planned Features:
- 🔄 Place orders (buy/sell)
- 🔄 Position management
- 🔄 Real-time price data
- 🔄 Trading strategies
- 🔄 Risk management
- 🔄 Portfolio tracking

## ❌ Troubleshooting

### Common Errors:

**"Invalid API-key, IP, or permissions for action"**
- Check if API key is correct
- Verify Futures trading permission is enabled
- Check IP whitelist settings
- Ensure using correct testnet/mainnet credentials

**"Timestamp for this request is outside of the recvWindow"**
- Check system time synchronization
- Verify internet connection

**"Signature for this request is not valid"**
- Check if secret key is correct
- Ensure no extra spaces in credentials

### Getting Help:

1. **Check logs** for detailed error messages
2. **Verify API credentials** are correct
3. **Test with testnet** first
4. **Check Binance API status** at [binance-docs.github.io](https://binance-docs.github.io/apidocs/futures/en/)

## 📚 Dependencies

- **[github.com/adshao/go-binance/v2](https://github.com/adshao/go-binance)** - Official Binance Go SDK
- **[github.com/joho/godotenv](https://github.com/joho/godotenv)** - Environment variable management
- **[github.com/thrasher-corp/gocryptotrader](https://github.com/thrasher-corp/gocryptotrader)** - Comprehensive crypto trading toolkit

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run tests and ensure they pass
6. Submit a pull request

## 📜 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

**This software is for educational purposes only. Trading cryptocurrencies involves substantial risk of loss. The authors are not responsible for any financial losses incurred while using this software. Always test with small amounts and use testnet for development.**
