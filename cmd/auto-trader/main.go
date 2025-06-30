package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/joho/godotenv"
	config "tread2/internal"
	"tread2/pkg/analysis"
	"tread2/pkg/trading"
)

// AI API structures
type DeepSeekRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
}

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type DeepSeekResponse struct {
	Choices []struct {
		Message Message `json:"message"`
	} `json:"choices"`
}

// AI Analysis Result
type AIAnalysisResult struct {
	Action         string  `json:"action"`          // "LONG", "SHORT", or "HOLD"
	Confidence     float64 `json:"confidence"`      // 0-100 (0 for HOLD)
	StopLoss       float64 `json:"stop_loss"`       // Percentage
	TakeProfit     float64 `json:"take_profit"`     // Percentage
	Reasoning      string  `json:"reasoning"`       // AI's reasoning
	RiskLevel      string  `json:"risk_level"`      // "LOW", "MEDIUM", "HIGH"
}

// CandleData represents candlestick data for AI analysis
type CandleData = analysis.CandleData

// AutoTrader represents the main trading bot
type AutoTrader struct {
	client      *trading.TradingClient
	config      *config.AppConfig
	minBalance  float64  // Minimum USDT balance required for trading
	symbols     []string // Symbols to trade
}

// NewAutoTrader creates a new auto trader instance
func NewAutoTrader() (*AutoTrader, error) {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: Could not load .env file: %v", err)
	}

	// Load configuration
	cfg := config.DefaultConfig()
	// cfg, err := config.LoadConfig("config.json")
	// if err != nil {
	//	return nil, fmt.Errorf("failed to load config: %w", err)
	// }

	// Create trading client
	client, err := trading.NewTradingClient()
	if err != nil {
		return nil, fmt.Errorf("failed to create trading client: %w", err)
	}

	// Default configuration
	minBalance := 50.0 // Minimum $50 USDT to trade
	if minBalanceStr := os.Getenv("MIN_BALANCE"); minBalanceStr != "" {
		if parsed, err := strconv.ParseFloat(minBalanceStr, 64); err == nil {
			minBalance = parsed
		}
	}

	symbols := []string{"BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"}
	if symbolsStr := os.Getenv("TRADING_SYMBOLS"); symbolsStr != "" {
		symbols = strings.Split(symbolsStr, ",")
	}

	return &AutoTrader{
		client:     client,
		config:     cfg,
		minBalance: minBalance,
		symbols:    symbols,
	}, nil
}

// checkBalance checks if there's enough balance for trading
func (at *AutoTrader) checkBalance() (bool, float64, error) {
	account, err := at.client.GetAccountInfoSimple()
	if err != nil {
		return false, 0, fmt.Errorf("failed to get account info: %w", err)
	}

	var usdtBalance float64
	for _, asset := range account.Assets {
		if asset.Asset == "USDT" {
			balance, err := strconv.ParseFloat(asset.WalletBalance, 64)
			if err != nil {
				continue
			}
			usdtBalance = balance
			break
		}
	}

	hasEnough := usdtBalance >= at.minBalance
	return hasEnough, usdtBalance, nil
}

// setupLeverageAndMargin ensures proper leverage and margin settings
func (at *AutoTrader) setupLeverageAndMargin(symbol string) error {
	// Check current leverage
	currentLeverage, err := at.client.GetLeverage(symbol)
	if err != nil {
		return fmt.Errorf("failed to get leverage for %s: %w", symbol, err)
	}

	// Set leverage to 10x if not already set
	if currentLeverage != 10 {
		if err := at.client.ChangeLeverage(symbol, 10); err != nil {
			return fmt.Errorf("failed to set leverage to 10x for %s: %w", symbol, err)
		}
		log.Printf("✅ Set leverage to 10x for %s", symbol)
	}

	// Check current margin mode
	currentMode, err := at.client.GetMarginMode(symbol)
	if err != nil {
		return fmt.Errorf("failed to get margin mode for %s: %w", symbol, err)
	}

	// Set margin mode to CROSS if not already set
	if currentMode != "CROSSED" {
		if err := at.client.ChangeMarginMode(symbol, "CROSSED"); err != nil {
			return fmt.Errorf("failed to set margin mode to CROSS for %s: %w", symbol, err)
		}
		log.Printf("✅ Set margin mode to CROSS for %s", symbol)
	}

	return nil
}

// getMarketData gets candlestick data for AI analysis
func (at *AutoTrader) getMarketData(symbol string) ([]CandleData, error) {
	klines, err := at.client.GetKlines(symbol, "1h", 100)
	if err != nil {
		return nil, fmt.Errorf("failed to get klines for %s: %w", symbol, err)
	}

	var candles []CandleData
	for _, kline := range klines {
		// kline is []interface{} with format: [OpenTime, Open, High, Low, Close, Volume, CloseTime]
		open, _ := strconv.ParseFloat(kline[1].(string), 64)
		high, _ := strconv.ParseFloat(kline[2].(string), 64)
		low, _ := strconv.ParseFloat(kline[3].(string), 64)
		close, _ := strconv.ParseFloat(kline[4].(string), 64)
		volume, _ := strconv.ParseFloat(kline[5].(string), 64)
		openTime := kline[0].(int64)

		candles = append(candles, CandleData{
			Timestamp: openTime,
			Open:      open,
			High:      high,
			Low:       low,
			Close:     close,
			Volume:    volume,
		})
	}

	return candles, nil
}

// analyzeWithAI sends market data to AI for analysis
func (at *AutoTrader) analyzeWithAI(symbol string, candles []CandleData) (*AIAnalysisResult, error) {
	apiKey := os.Getenv("DEEPSEEK_API_KEY")
	if apiKey == "" {
		return nil, fmt.Errorf("DEEPSEEK_API_KEY not set")
	}

	// Prepare market data summary
	if len(candles) < 20 {
		return nil, fmt.Errorf("insufficient market data")
	}

	latest := candles[len(candles)-1]
	prev := candles[len(candles)-2]
	
	priceChange := ((latest.Close - prev.Close) / prev.Close) * 100
	
	// Get technical indicators
	breakoutData := analysis.DetectBreakouts(symbol, candles, 14, 2.0)
	
	prompt := fmt.Sprintf(`
You are a professional cryptocurrency trading advisor. Analyze the following market data for %s and provide trading recommendations.

CURRENT MARKET DATA:
- Current Price: $%.2f
- Price Change (1h): %.2f%%
- 24h High: $%.2f
- 24h Low: $%.2f
- Volume: %.2f

TECHNICAL ANALYSIS:
- Breakout Signal: %v
- Market Trend: %s

INSTRUCTIONS:
1. Analyze the technical indicators and market conditions
2. Provide a trading signal: LONG, SHORT, or HOLD
3. If LONG/SHORT, provide confidence score (1-100)
4. If HOLD, set confidence to 0
5. Suggest stop loss and take profit percentages
6. Explain your reasoning

Please respond in JSON format:
{
  "action": "LONG|SHORT|HOLD",
  "confidence": 0-100,
  "stop_loss": percentage,
  "take_profit": percentage,  
  "reasoning": "your analysis",
  "risk_level": "LOW|MEDIUM|HIGH"
}

Consider:
- Current market volatility
- Technical indicators strength
- Risk management
- Only recommend high-confidence trades (confidence > 70)
`, symbol, latest.Close, priceChange, latest.High, latest.Low, latest.Volume, 
   breakoutData.HasBreakout, breakoutData.Direction)

	reqBody := DeepSeekRequest{
		Model: "deepseek-chat",
		Messages: []Message{
			{Role: "user", Content: prompt},
		},
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequest("POST", "https://api.deepseek.com/chat/completions", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to call AI API: %w", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("AI API error (%d): %s", resp.StatusCode, string(body))
	}

	var aiResp DeepSeekResponse
	if err := json.Unmarshal(body, &aiResp); err != nil {
		return nil, fmt.Errorf("failed to unmarshal AI response: %w", err)
	}

	if len(aiResp.Choices) == 0 {
		return nil, fmt.Errorf("no AI response received")
	}

	// Parse AI response
	content := aiResp.Choices[0].Message.Content
	
	// Extract JSON from AI response
	startIdx := strings.Index(content, "{")
	endIdx := strings.LastIndex(content, "}")
	if startIdx == -1 || endIdx == -1 {
		return nil, fmt.Errorf("invalid AI response format")
	}
	
	jsonStr := content[startIdx : endIdx+1]
	
	var result AIAnalysisResult
	if err := json.Unmarshal([]byte(jsonStr), &result); err != nil {
		return nil, fmt.Errorf("failed to parse AI analysis: %w", err)
	}

	return &result, nil
}

// calculatePositionSize calculates position size based on balance and risk
func (at *AutoTrader) calculatePositionSize(balance float64, price float64, riskPercent float64) float64 {
	// Use fixed $15 margin for position
	maxUSDT := 15.0
	
	// Calculate position size considering leverage (10x)
	leveragedAmount := maxUSDT * 10
	
	// Apply risk management (max 5% risk per trade)
	if riskPercent > 5.0 {
		riskPercent = 5.0
	}
	
	riskAmount := balance * (riskPercent / 100)
	positionValue := math.Min(leveragedAmount, riskAmount*10) // 10x leverage
	
	quantity := positionValue / price
	
	// Round to reasonable precision
	return math.Floor(quantity*1000) / 1000
}

// openPosition opens a trading position with stop loss and take profit
func (at *AutoTrader) openPosition(symbol string, analysis *AIAnalysisResult, balance float64) error {
	// Get current price
	ticker, err := at.client.GetTicker(symbol)
	if err != nil {
		return fmt.Errorf("failed to get ticker for %s: %w", symbol, err)
	}
	
	currentPrice, err := strconv.ParseFloat(ticker.Price, 64)
	if err != nil {
		return fmt.Errorf("failed to parse price: %w", err)
	}

	// Calculate position size
	quantity := at.calculatePositionSize(balance, currentPrice, 3.0) // 3% risk per trade
	
	if quantity <= 0 {
		return fmt.Errorf("calculated position size too small")
	}

	// Determine side
	side := "BUY"
	if analysis.Action == "SHORT" {
		side = "SELL"
	}

	// Calculate stop loss and take profit prices
	var stopPrice, takeProfitPrice float64
	if analysis.Action == "LONG" {
		stopPrice = currentPrice * (1 - analysis.StopLoss/100)
		takeProfitPrice = currentPrice * (1 + analysis.TakeProfit/100)
	} else {
		stopPrice = currentPrice * (1 + analysis.StopLoss/100)
		takeProfitPrice = currentPrice * (1 - analysis.TakeProfit/100)
	}

	log.Printf("🔥 Opening %s position for %s", analysis.Action, symbol)
	log.Printf("   Price: $%.4f", currentPrice)
	log.Printf("   Quantity: %.3f", quantity)
	log.Printf("   Stop Loss: $%.4f (%.2f%%)", stopPrice, analysis.StopLoss)
	log.Printf("   Take Profit: $%.4f (%.2f%%)", takeProfitPrice, analysis.TakeProfit)
	log.Printf("   Confidence: %.1f%%", analysis.Confidence)
	log.Printf("   Risk Level: %s", analysis.RiskLevel)

	// Open main position
	order, err := at.client.CreateOrder(&trading.OrderRequest{
		Symbol:   symbol,
		Side:     side,
		Type:     "MARKET",
		Quantity: fmt.Sprintf("%.3f", quantity),
	})
	if err != nil {
		return fmt.Errorf("failed to create market order: %w", err)
	}

	log.Printf("✅ Market order executed: %s", order.OrderID)

	// Set stop loss order  
	stopSide := "SELL"
	if analysis.Action == "SHORT" {
		stopSide = "BUY"
	}
	
	stopOrder, err := at.client.CreateOrder(&trading.OrderRequest{
		Symbol:        symbol,
		Side:          stopSide,
		Type:          "STOP_MARKET",
		Quantity:      fmt.Sprintf("%.3f", quantity),
		StopPrice:     fmt.Sprintf("%.4f", stopPrice),
		ClosePosition: true,
	})
	if err != nil {
		log.Printf("⚠️  Failed to set stop loss: %v", err)
	} else {
		log.Printf("✅ Stop loss order set: %s", stopOrder.OrderID)
	}

	// Set take profit order
	tpOrder, err := at.client.CreateOrder(&trading.OrderRequest{
		Symbol:        symbol,
		Side:          stopSide,
		Type:          "TAKE_PROFIT_MARKET", 
		Quantity:      fmt.Sprintf("%.3f", quantity),
		StopPrice:     fmt.Sprintf("%.4f", takeProfitPrice),
		ClosePosition: true,
	})
	if err != nil {
		log.Printf("⚠️  Failed to set take profit: %v", err)
	} else {
		log.Printf("✅ Take profit order set: %s", tpOrder.OrderID)
	}

	log.Printf("💡 Reasoning: %s", analysis.Reasoning)
	
	return nil
}

// processSymbol processes a single trading symbol
func (at *AutoTrader) processSymbol(symbol string, balance float64) error {
	log.Printf("📊 Analyzing %s...", symbol)

	// Setup leverage and margin
	if err := at.setupLeverageAndMargin(symbol); err != nil {
		return fmt.Errorf("failed to setup leverage/margin for %s: %w", symbol, err)
	}

	// Get market data
	candles, err := at.getMarketData(symbol)
	if err != nil {
		return fmt.Errorf("failed to get market data for %s: %w", symbol, err)
	}

	// Analyze with AI
	analysis, err := at.analyzeWithAI(symbol, candles)
	if err != nil {
		return fmt.Errorf("failed to analyze %s with AI: %w", symbol, err)
	}

	log.Printf("🤖 AI Analysis for %s:", symbol)
	log.Printf("   Action: %s", analysis.Action)
	log.Printf("   Confidence: %.1f%%", analysis.Confidence)
	log.Printf("   Risk Level: %s", analysis.RiskLevel)

	// Check if we should trade
	if analysis.Action == "HOLD" || analysis.Confidence < 70 {
		log.Printf("⏸️  Skipping %s - %s with %.1f%% confidence", symbol, analysis.Action, analysis.Confidence)
		return nil
	}

	// Open position
	if err := at.openPosition(symbol, analysis, balance); err != nil {
		return fmt.Errorf("failed to open position for %s: %w", symbol, err)
	}

	return nil
}

// waitUntilNextHour waits until the next hour (minute 1)
func (at *AutoTrader) waitUntilNextHour() {
	now := time.Now()
	nextHour := now.Truncate(time.Hour).Add(time.Hour).Add(1 * time.Minute)
	duration := nextHour.Sub(now)
	
	log.Printf("⏰ Waiting until next hour: %s (%.0f minutes)", 
		nextHour.Format("15:04"), duration.Minutes())
	
	time.Sleep(duration)
}

// scanForRetestSymbols scans for symbols with successful retest patterns
func (at *AutoTrader) scanForRetestSymbols() ([]string, error) {
	log.Printf("🔍 Scanning for symbols with successful retest patterns...")

	// Get all USDT symbols
	symbols, err := at.client.GetUSDTSymbols()
	if err != nil {
		return nil, fmt.Errorf("failed to get USDT symbols: %w", err)
	}

	var retestSymbols []string
	var totalScanned int
	var successfulRetests int

	log.Printf("📊 Found %d USDT pairs to analyze", len(symbols))

	for i, symbol := range symbols {
		totalScanned++
		
		// Progress logging every 50 symbols
		if i%50 == 0 {
			log.Printf("📈 Progress: %d/%d symbols scanned", i, len(symbols))
		}

		// Get kline data for analysis
		klines, err := at.client.GetKlines(symbol, "1h", 100)
		if err != nil {
			continue // Skip symbols with data issues
		}

		// Convert to CandleData format for analysis
		candles, err := at.convertKlinesToCandles(klines)
		if err != nil {
			continue
		}

		// Check if this symbol has successful retest
		if at.hasSuccessfulRetest(symbol, candles) {
			retestSymbols = append(retestSymbols, symbol)
			successfulRetests++
			// Log success but limit excessive output
			if successfulRetests <= 20 {
				log.Printf("✅ Found successful retest: %s", symbol)
			} else if successfulRetests%10 == 0 {
				log.Printf("✅ Found %d successful retests so far...", successfulRetests)
			}
		}

		// Small delay to avoid overwhelming the API
		time.Sleep(100 * time.Millisecond)
	}

	log.Printf("📊 Scan completed:")
	log.Printf("   Total symbols scanned: %d", totalScanned)
	log.Printf("   Symbols with successful retests: %d", successfulRetests)
	log.Printf("   Selected for AI analysis: %v", retestSymbols)

	return retestSymbols, nil
}

// convertKlinesToCandles converts kline data to CandleData format
func (at *AutoTrader) convertKlinesToCandles(klines [][]interface{}) ([]CandleData, error) {
	var candles []CandleData
	for _, kline := range klines {
		open, _ := strconv.ParseFloat(kline[1].(string), 64)
		high, _ := strconv.ParseFloat(kline[2].(string), 64)
		low, _ := strconv.ParseFloat(kline[3].(string), 64)
		close, _ := strconv.ParseFloat(kline[4].(string), 64)
		volume, _ := strconv.ParseFloat(kline[5].(string), 64)
		openTime := kline[0].(int64)

		candles = append(candles, CandleData{
			Timestamp: openTime,
			Open:      open,
			High:      high,
			Low:       low,
			Close:     close,
			Volume:    volume,
		})
	}
	return candles, nil
}

// hasSuccessfulRetest checks if a symbol has successful retest pattern
func (at *AutoTrader) hasSuccessfulRetest(symbol string, candles []CandleData) bool {
	if len(candles) < 20 {
		return false
	}

	// Use technical analyzer to detect patterns
	analyzer := analysis.NewTechnicalAnalyzer()
	
	// Convert to Kline format for technical analysis
	klines := make([]*analysis.Kline, len(candles))
	for i, candle := range candles {
		klines[i] = &analysis.Kline{
			OpenTime:  candle.Timestamp,
			Open:      candle.Open,
			High:      candle.High,
			Low:       candle.Low,
			Close:     candle.Close,
			Volume:    candle.Volume,
			CloseTime: candle.Timestamp + 3600000,
			IsGreen:   candle.Close > candle.Open,
			IsRed:     candle.Close < candle.Open,
		}
	}

	// Get breakout signals
	signals := analyzer.DetectBreakouts(klines, symbol)

	// Check for successful retest patterns
	for _, signal := range signals {
		if signal.Type == "RETEST_SUCCESS" && signal.Confidence > 60.0 {
			return true
		}
	}

	// Alternative check using basic breakout analysis
	breakoutData := analysis.DetectBreakouts(symbol, candles, 14, 2.0)
	if breakoutData.HasBreakout && breakoutData.Confidence > 60.0 {
		return true
	}

	return false
}

// run starts the main trading loop
func (at *AutoTrader) run() {
	log.Printf("🚀 Auto Trader Bot Started!")
	log.Printf("� Will scan ALL USDT pairs for successful retest patterns")
	log.Printf("💰 Minimum balance: $%.2f USDT", at.minBalance)
	log.Printf("⚙️  Leverage: 10x, Margin: CROSS")
	
	for {
		startTime := time.Now()
		log.Printf("\n" + strings.Repeat("=", 60))
		log.Printf("🔄 Starting trading cycle at %s", startTime.Format("2006-01-02 15:04:05"))
		log.Printf(strings.Repeat("=", 60))

		// Check balance first
		hasEnoughBalance, balance, err := at.checkBalance()
		if err != nil {
			log.Printf("❌ Failed to check balance: %v", err)
		} else if !hasEnoughBalance {
			log.Printf("💸 Insufficient balance: $%.2f USDT (minimum: $%.2f)", balance, at.minBalance)
			log.Printf("⏭️  Skipping this cycle...")
		} else {
			log.Printf("💰 Available balance: $%.2f USDT", balance)
			
			// Scan for symbols with successful retest patterns
			retestSymbols, err := at.scanForRetestSymbols()
			if err != nil {
				log.Printf("❌ Error scanning for retest symbols: %v", err)
			} else if len(retestSymbols) == 0 {
				log.Printf("🔍 No symbols found with successful retest patterns")
			} else {
				log.Printf("📈 Found %d symbols with successful retests", len(retestSymbols))
				
				// Analyze ALL symbols with successful retest (no limit)
				log.Printf("🤖 Proceeding with AI analysis for ALL %d quality coins...", len(retestSymbols))
				
				// Process each symbol with retest pattern
				for i, symbol := range retestSymbols {
					log.Printf("\n🔍 [%d/%d] Analyzing %s with AI...", i+1, len(retestSymbols), symbol)
					
					if err := at.processSymbol(symbol, balance); err != nil {
						log.Printf("❌ Error processing %s: %v", symbol, err)
					}
					
					// Small delay between symbols
					time.Sleep(2 * time.Second)
				}
			}
		}

		log.Printf("\n✅ Trading cycle completed in %.1f seconds", time.Since(startTime).Seconds())
		
		// Wait until next hour
		at.waitUntilNextHour()
	}
}

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	
	// Create auto trader
	trader, err := NewAutoTrader()
	if err != nil {
		log.Fatalf("Failed to create auto trader: %v", err)
	}

	// Start trading
	trader.run()
}
