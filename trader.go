package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	config "tread2/internal"
	"tread2/pkg/trading"

	"github.com/joho/godotenv"
	"github.com/adshao/go-binance/v2/futures"
)

// AI API structures
type DeepSeekRequest struct {
	Model       string    `json:"model"`
	Messages    []Message `json:"messages"`
	Temperature float64   `json:"temperature"`
	MaxTokens   int       `json:"max_tokens"`
}

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type DeepSeekResponse struct {
	Choices []struct {
		Message Message `json:"message"`
	} `json:"choices"`
	Error struct {
		Message string `json:"message"`
	} `json:"error"`
}

// CandleData represents candlestick data for AI analysis
type CandleData struct {
	Timestamp int64   `json:"timestamp"`
	Open      float64 `json:"open"`
	High      float64 `json:"high"`
	Low       float64 `json:"low"`
	Close     float64 `json:"close"`
	Volume    float64 `json:"volume"`
}

// TradingSignal represents AI trading recommendation
type TradingSignal struct {
	Symbol       string  `json:"symbol"`
	Action       string  `json:"action"`     // LONG, SHORT, HOLD
	Confidence   int     `json:"confidence"` // 0-100%
	CurrentPrice float64 `json:"current_price"`
	StopLoss     float64 `json:"stop_loss"`
	TakeProfit   float64 `json:"take_profit"`
	Analysis     string  `json:"analysis"`
}

// BreakoutSignal represents support/resistance breakout analysis
type BreakoutSignal struct {
	Symbol          string      `json:"symbol"`
	CurrentPrice    float64     `json:"current_price"`
	SupportLevel    float64     `json:"support_level"`
	ResistanceLevel float64     `json:"resistance_level"`
	PreviousCandle  *CandleData `json:"previous_candle"`
	CurrentCandle   *CandleData `json:"current_candle"`
	BreakoutType    string      `json:"breakout_type"`    // "SUPPORT_BREAK", "RESISTANCE_BREAK", "NONE"
	Signal          string      `json:"signal"`           // "LONG", "SHORT", "NONE"
	StopLoss        float64     `json:"stop_loss"`        // Low for LONG, High for SHORT
	TakeProfit      float64     `json:"take_profit"`      // AI-enhanced target
	Confidence      float64     `json:"confidence"`       // 0-100
	Analysis        string      `json:"analysis"`
}

// SupportResistanceLevel represents a support or resistance level
type SupportResistanceLevel struct {
	Level    float64 `json:"level"`
	Type     string  `json:"type"`      // "SUPPORT", "RESISTANCE"
	Strength float64 `json:"strength"`  // 0-100
	Touches  int     `json:"touches"`   // Number of times price touched this level
}

// FibonacciLevels represents Fibonacci retracement levels
type FibonacciLevels struct {
	High      float64 `json:"high"`
	Low       float64 `json:"low"`
	Level236  float64 `json:"level_236"`
	Level382  float64 `json:"level_382"`
	Level500  float64 `json:"level_500"`
	Level618  float64 `json:"level_618"`
	Level786  float64 `json:"level_786"`
	Direction string  `json:"direction"` // "UP", "DOWN"
}

// scanForBreakouts scans for breakout signals
func scanForBreakouts(tradingClient *trading.TradingClient, symbols []string) ([]*BreakoutSignal, error) {
	var breakoutSignals []*BreakoutSignal

	fmt.Printf("🔍 Scanning %d symbols for breakout signals...\n", len(symbols))

	for _, symbol := range symbols {
		// Get hourly candlestick data for breakout analysis
		candleData, err := getBreakoutCandlestickData(tradingClient, symbol, 200)
		if err != nil {
			log.Printf("Failed to get candle data for %s: %v", symbol, err)
			continue
		}

		// Analyze breakout signal
		breakoutSignal, err := analyzeBreakoutSignal(candleData, symbol)
		if err != nil {
			log.Printf("Failed to analyze breakout for %s: %v", symbol, err)
			continue
		}

		// Only add signals that have actual breakouts
		if breakoutSignal.Signal != "NONE" {
			breakoutSignals = append(breakoutSignals, breakoutSignal)
			fmt.Printf("🚨 Breakout detected: %s - %s\n", symbol, breakoutSignal.Signal)
		}
	}

	return breakoutSignals, nil
}

// main trading loop with breakout logic
func startBreakoutTrading(tradingClient *trading.TradingClient, symbols []string) {
	fmt.Printf("🚀 Starting Professional Breakout Trading System...\n")
	fmt.Printf("📊 Monitoring %d symbols for breakout opportunities\n", len(symbols))

	// Run initial scan immediately
	runBreakoutScan(tradingClient, symbols)

	ticker := time.NewTicker(5 * time.Minute) // Check every 5 minutes
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			runBreakoutScan(tradingClient, symbols)
		}
	}
}

// runBreakoutScan performs a single breakout scan
func runBreakoutScan(tradingClient *trading.TradingClient, symbols []string) {
	fmt.Print("\n" + strings.Repeat("=", 80) + "\n")
	fmt.Printf("🔍 Scanning for breakout signals - %s\n", time.Now().Format("2006-01-02 15:04:05"))
	fmt.Print(strings.Repeat("=", 80) + "\n")

	// Check current positions and cleanup if needed
	// err := tradingClient.CleanupOldPositions()
	// if err != nil {
	// 	log.Printf("Failed to cleanup positions: %v", err)
	// }

	// Get current balance
	balance, err := tradingClient.GetBalance(context.Background())
	if err != nil {
		log.Printf("Failed to get balance: %v", err)
		return
	}

	// Calculate USDT balance
	var balanceUSDT float64
	for _, asset := range balance {
		if asset.Asset == "USDT" {
			balanceUSDT, _ = strconv.ParseFloat(asset.WalletBalance, 64)
			break
		}
	}

	fmt.Printf("💰 Current Balance: %.2f USDT\n", balanceUSDT)

	// Scan for breakout signals
	breakoutSignals, err := scanForBreakouts(tradingClient, symbols)
	if err != nil {
		log.Printf("Failed to scan for breakouts: %v", err)
		return
	}

	if len(breakoutSignals) == 0 {
		fmt.Printf("⚪ No breakout signals detected\n")
		return
	}

	// Display breakout analysis
	displayBreakoutAnalysis(breakoutSignals)

	// Process each breakout signal
	for _, breakoutSignal := range breakoutSignals {
		fmt.Printf("\n🤖 Analyzing breakout signal with AI: %s\n", breakoutSignal.Symbol)

		// Get AI analysis and confirmation
		candleData, err := getBreakoutCandlestickData(tradingClient, breakoutSignal.Symbol, 100)
		if err != nil {
			log.Printf("Failed to get candle data for AI analysis: %v", err)
			continue
		}

		aiSignal, err := callAIForBreakoutAnalysis(breakoutSignal, candleData)
		if err != nil {
			log.Printf("Failed to get AI analysis: %v", err)
			continue
		}

		// Display AI recommendation
		displayAIRecommendation(aiSignal)

		// Execute trade if AI confirms
		if aiSignal.Action == breakoutSignal.Signal && aiSignal.Confidence >= 70 {
			fmt.Printf("✅ AI confirms breakout signal! Executing trade...\n")

			// Update breakout signal with AI-enhanced targets
			breakoutSignal.StopLoss = aiSignal.StopLoss
			breakoutSignal.TakeProfit = aiSignal.TakeProfit

			success, err := executeBreakoutTrade(context.Background(), tradingClient, breakoutSignal, balanceUSDT)
			if err != nil {
				log.Printf("Failed to execute breakout trade: %v", err)
				continue
			}

			if success {
				fmt.Printf("🎉 Breakout trade executed successfully!\n")
			}
		} else {
			fmt.Printf("❌ AI does not confirm breakout signal (AI: %s, Confidence: %d%%)\n", 
				aiSignal.Action, aiSignal.Confidence)
		}
	}
}

// displayBreakoutAnalysis displays breakout analysis results
func displayBreakoutAnalysis(signals []*BreakoutSignal) {
	if len(signals) == 0 {
		return
	}

	fmt.Print("\n🎯 BREAKOUT ANALYSIS RESULTS\n")
	fmt.Print(strings.Repeat("=", 80) + "\n")

	for _, signal := range signals {
		var signalColor string
		switch signal.Signal {
		case "LONG":
			signalColor = "🟢 LONG"
		case "SHORT":
			signalColor = "🔴 SHORT"
		default:
			signalColor = "⚪ HOLD"
		}

		fmt.Printf("📈 %s | %s | $%.4f | Confidence: %.0f%%\n",
			signal.Symbol, signalColor, signal.CurrentPrice, signal.Confidence)
		fmt.Printf("   🎯 Support: %.4f | Resistance: %.4f\n",
			signal.SupportLevel, signal.ResistanceLevel)
		fmt.Printf("   ⚠️  Stop Loss: %.4f | Breakout Type: %s\n",
			signal.StopLoss, signal.BreakoutType)
		fmt.Printf("   💡 Analysis: %s\n", signal.Analysis)
		fmt.Printf("\n")
	}
}

// displayAIRecommendation displays AI trading recommendation
func displayAIRecommendation(signal *TradingSignal) {
	fmt.Print("\n🤖 AI TRADING RECOMMENDATION\n")
	fmt.Print(strings.Repeat("-", 50) + "\n")

	var actionColor string
	switch signal.Action {
	case "LONG":
		actionColor = "🟢 LONG"
	case "SHORT":
		actionColor = "🔴 SHORT"
	default:
		actionColor = "⚪ HOLD"
	}

	fmt.Printf("Symbol: %s\n", signal.Symbol)
	fmt.Printf("Action: %s\n", actionColor)
	fmt.Printf("Confidence: %d%%\n", signal.Confidence)
	fmt.Printf("Current Price: $%.4f\n", signal.CurrentPrice)
	fmt.Printf("Stop Loss: $%.4f\n", signal.StopLoss)
	fmt.Printf("Take Profit: $%.4f\n", signal.TakeProfit)
	fmt.Printf("Analysis: %s\n", signal.Analysis)
	fmt.Print(strings.Repeat("-", 50) + "\n")
}

// getBreakoutCandlestickData gets hourly candlestick data for breakout analysis
func getBreakoutCandlestickData(tradingClient *trading.TradingClient, symbol string, limit int) ([]*CandleData, error) {
	klines, err := tradingClient.BinanceClient.NewKlinesService().
		Symbol(symbol).
		Interval("1h"). // 1-hour timeframe for breakout detection
		Limit(limit).
		Do(context.Background())

	if err != nil {
		return nil, err
	}

	var candleData []*CandleData
	for _, kline := range klines {
		open, _ := strconv.ParseFloat(kline.Open, 64)
		high, _ := strconv.ParseFloat(kline.High, 64)
		low, _ := strconv.ParseFloat(kline.Low, 64)
		close, _ := strconv.ParseFloat(kline.Close, 64)
		volume, _ := strconv.ParseFloat(kline.Volume, 64)

		candleData = append(candleData, &CandleData{
			Timestamp: kline.OpenTime,
			Open:      open,
			High:      high,
			Low:       low,
			Close:     close,
			Volume:    volume,
		})
	}

	return candleData, nil
}

// analyzeBreakoutSignal analyzes support/resistance breakout signals
func analyzeBreakoutSignal(candleData []*CandleData, symbol string) (*BreakoutSignal, error) {
	if len(candleData) < 50 {
		return nil, fmt.Errorf("insufficient data for breakout analysis")
	}

	// Get current and previous candles
	currentCandle := candleData[len(candleData)-1]
	previousCandle := candleData[len(candleData)-2]

	// Calculate support and resistance levels from recent history
	supportLevel, resistanceLevel := calculateSupportResistanceLevels(candleData)

	signal := &BreakoutSignal{
		Symbol:          symbol,
		CurrentPrice:    currentCandle.Close,
		SupportLevel:    supportLevel,
		ResistanceLevel: resistanceLevel,
		PreviousCandle:  previousCandle,
		CurrentCandle:   currentCandle,
		BreakoutType:    "NONE",
		Signal:          "NONE",
		StopLoss:        0,
		TakeProfit:      0,
		Confidence:      0,
		Analysis:        "",
	}

	// Check for support breakout (bearish signal)
	if previousCandle.Close > supportLevel && // Previous candle was above support
		previousCandle.Close > previousCandle.Open && // Previous candle was green
		currentCandle.Close < supportLevel { // Current candle broke below support

		signal.BreakoutType = "SUPPORT_BREAK"
		signal.Signal = "LONG" // Wait for LONG signal as per new logic
		signal.StopLoss = currentCandle.Low // Stop loss at current candle's low
		signal.Confidence = 75
		signal.Analysis = fmt.Sprintf("Support breakout detected: Previous green candle at %.4f above support %.4f, current candle broke below to %.4f",
			previousCandle.Close, supportLevel, currentCandle.Close)
	}

	// Check for resistance breakout (bullish signal)
	if previousCandle.Close < resistanceLevel && // Previous candle was below resistance
		previousCandle.Close < previousCandle.Open && // Previous candle was red
		currentCandle.Close > resistanceLevel { // Current candle broke above resistance

		signal.BreakoutType = "RESISTANCE_BREAK"
		signal.Signal = "SHORT" // Wait for SHORT signal as per new logic
		signal.StopLoss = currentCandle.High // Stop loss at current candle's high
		signal.Confidence = 75
		signal.Analysis = fmt.Sprintf("Resistance breakout detected: Previous red candle at %.4f below resistance %.4f, current candle broke above to %.4f",
			previousCandle.Close, resistanceLevel, currentCandle.Close)
	}

	return signal, nil
}

// calculateSupportResistanceLevels calculates support and resistance levels from price history
func calculateSupportResistanceLevels(candleData []*CandleData) (float64, float64) {
	if len(candleData) < 20 {
		return 0, 0
	}

	// Use last 50 candles for S/R calculation
	period := 50
	if len(candleData) < period {
		period = len(candleData)
	}

	recentData := candleData[len(candleData)-period:]

	// Find pivot highs and lows
	var pivotHighs, pivotLows []float64

	for i := 2; i < len(recentData)-2; i++ {
		// Pivot high: higher than 2 candles on each side
		if recentData[i].High > recentData[i-1].High && recentData[i].High > recentData[i-2].High &&
			recentData[i].High > recentData[i+1].High && recentData[i].High > recentData[i+2].High {
			pivotHighs = append(pivotHighs, recentData[i].High)
		}

		// Pivot low: lower than 2 candles on each side
		if recentData[i].Low < recentData[i-1].Low && recentData[i].Low < recentData[i-2].Low &&
			recentData[i].Low < recentData[i+1].Low && recentData[i].Low < recentData[i+2].Low {
			pivotLows = append(pivotLows, recentData[i].Low)
		}
	}

	// Calculate support (recent significant low)
	var supportLevel float64
	if len(pivotLows) > 0 {
		// Use the most recent significant low
		supportLevel = pivotLows[len(pivotLows)-1]

		// If multiple lows are close, use the average
		tolerance := supportLevel * 0.01 // 1% tolerance
		var closeLows []float64
		for _, low := range pivotLows {
			if math.Abs(low-supportLevel) <= tolerance {
				closeLows = append(closeLows, low)
			}
		}

		if len(closeLows) > 1 {
			sum := 0.0
			for _, low := range closeLows {
				sum += low
			}
			supportLevel = sum / float64(len(closeLows))
		}
	}

	// Calculate resistance (recent significant high)
	var resistanceLevel float64
	if len(pivotHighs) > 0 {
		// Use the most recent significant high
		resistanceLevel = pivotHighs[len(pivotHighs)-1]

		// If multiple highs are close, use the average
		tolerance := resistanceLevel * 0.01 // 1% tolerance
		var closeHighs []float64
		for _, high := range pivotHighs {
			if math.Abs(high-resistanceLevel) <= tolerance {
				closeHighs = append(closeHighs, high)
			}
		}

		if len(closeHighs) > 1 {
			sum := 0.0
			for _, high := range closeHighs {
				sum += high
			}
			resistanceLevel = sum / float64(len(closeHighs))
		}
	}

	return supportLevel, resistanceLevel
}

// executeBreakoutTrade executes a breakout trade with AI confirmation
func executeBreakoutTrade(ctx context.Context, tradingClient *trading.TradingClient, breakoutSignal *BreakoutSignal, balanceUSDT float64) (bool, error) {
	// Check margin balance first
	marginAmount := 3.0 // $3 per trade
	effectiveBalance := balanceUSDT

	if effectiveBalance < marginAmount {
		return false, fmt.Errorf("insufficient balance: %.2f USDT margin balance, %.2f USDT needed", effectiveBalance, marginAmount)
	}

	// Set conservative leverage for breakout trades
	err := tradingClient.SetLeverage(breakoutSignal.Symbol, 3)
	if err != nil {
		return false, fmt.Errorf("failed to set leverage: %v", err)
	}

	// Calculate position size
	positionValue := marginAmount * 3 // 3x leverage
	quantity := positionValue / breakoutSignal.CurrentPrice

	// Format quantity according to symbol precision
	quantity = formatQuantity(breakoutSignal.Symbol, quantity)

	fmt.Printf("📏 Position Size: %s %s\n", formatQuantityString(breakoutSignal.Symbol, quantity), strings.Replace(breakoutSignal.Symbol, "USDT", "", 1))
	fmt.Printf("💼 Position Value: $%.2f\n", positionValue)

	// Place market order with enhanced precision handling
	var side futures.SideType
	if breakoutSignal.Signal == "SHORT" {
		side = futures.SideTypeSell
	} else {
		side = futures.SideTypeBuy
	}

	// Try multiple methods to place the order
	orderResult, err := placeOrderWithRetry(ctx, tradingClient, breakoutSignal.Symbol, side, quantity)
	if err != nil {
		return false, fmt.Errorf("failed to place order after all attempts: %v", err)
	}

	fmt.Printf("✅ Order placed successfully! Order ID: %d\n", orderResult.OrderID)

	// Set stop loss and take profit with AI-enhanced levels
	err = setBreakoutStopLossAndTakeProfit(ctx, tradingClient, breakoutSignal, quantity)
	if err != nil {
		fmt.Printf("⚠️ Warning: Failed to set stop loss/take profit: %v", err)
	}

	return true, nil
}

// setBreakoutStopLossAndTakeProfit sets protective orders for breakout trades
func setBreakoutStopLossAndTakeProfit(ctx context.Context, tradingClient *trading.TradingClient, breakoutSignal *BreakoutSignal, quantity float64) error {
	// Stop Loss Order
	var stopSide futures.SideType
	if breakoutSignal.Signal == "SHORT" {
		stopSide = futures.SideTypeBuy
	} else {
		stopSide = futures.SideTypeSell
	}

	// Try to place stop loss with enhanced precision
	quantityStr, err := tradingClient.FormatQuantity(ctx, breakoutSignal.Symbol, quantity)
	if err != nil {
		quantityStr = fmt.Sprintf("%.3f", quantity) // fallback
	}

	stopPriceStr, err := tradingClient.FormatPrice(ctx, breakoutSignal.Symbol, breakoutSignal.StopLoss)
	if err != nil {
		stopPriceStr = fmt.Sprintf("%.4f", breakoutSignal.StopLoss) // fallback
	}

	_, err = tradingClient.BinanceClient.NewCreateOrderService().
		Symbol(breakoutSignal.Symbol).
		Side(stopSide).
		Type("STOP_MARKET").
		Quantity(quantityStr).
		StopPrice(stopPriceStr).
		ReduceOnly(true).
		Do(ctx)

	if err != nil {
		return fmt.Errorf("failed to set stop loss: %v", err)
	}

	// Take Profit Order - use AI-enhanced target if available
	var takeProfitPrice float64
	if breakoutSignal.TakeProfit > 0 {
		takeProfitPrice = breakoutSignal.TakeProfit
	} else {
		// Fallback to 2:1 R/R ratio
		if breakoutSignal.Signal == "LONG" {
			risk := breakoutSignal.CurrentPrice - breakoutSignal.StopLoss
			takeProfitPrice = breakoutSignal.CurrentPrice + (risk * 2)
		} else {
			risk := breakoutSignal.StopLoss - breakoutSignal.CurrentPrice
			takeProfitPrice = breakoutSignal.CurrentPrice - (risk * 2)
		}
	}

	takeProfitPriceStr, err := tradingClient.FormatPrice(ctx, breakoutSignal.Symbol, takeProfitPrice)
	if err != nil {
		takeProfitPriceStr = fmt.Sprintf("%.4f", takeProfitPrice) // fallback
	}

	_, err = tradingClient.BinanceClient.NewCreateOrderService().
		Symbol(breakoutSignal.Symbol).
		Side(stopSide).
		Type("LIMIT").
		Quantity(quantityStr).
		Price(takeProfitPriceStr).
		TimeInForce("GTC").
		ReduceOnly(true).
		Do(ctx)

	if err != nil {
		return fmt.Errorf("failed to set take profit: %v", err)
	}

	fmt.Printf("✅ Stop Loss (%.4f) and Take Profit (%.4f) orders set\n", breakoutSignal.StopLoss, takeProfitPrice)
	return nil
}

// callAIForBreakoutAnalysis calls AI to analyze breakout signal and get enhanced targets
func callAIForBreakoutAnalysis(breakoutSignal *BreakoutSignal, candleData []*CandleData) (*TradingSignal, error) {
	// Calculate Fibonacci levels for the breakout
	fibonacci := calculateFibonacci(candleData)

	// Prepare AI prompt with breakout analysis
	prompt := fmt.Sprintf(`
BREAKOUT ANALYSIS REQUEST for %s

BREAKOUT DETAILS:
- Symbol: %s
- Current Price: %.4f
- Breakout Type: %s
- Signal: %s
- Support Level: %.4f
- Resistance Level: %.4f
- Stop Loss: %.4f
- Confidence: %.0f%%

PREVIOUS CANDLE:
- Open: %.4f, High: %.4f, Low: %.4f, Close: %.4f
- Color: %s

CURRENT CANDLE:
- Open: %.4f, High: %.4f, Low: %.4f, Close: %.4f
- Color: %s

FIBONACCI LEVELS:
- High: %.4f, Low: %.4f
- 23.6%%: %.4f
- 38.2%%: %.4f
- 50.0%%: %.4f
- 61.8%%: %.4f
- 78.6%%: %.4f
- Direction: %s

ANALYSIS SUMMARY:
%s

Please analyze this breakout signal and provide:
1. Your confidence level (0-100%%)
2. Recommended action: LONG, SHORT, or HOLD
3. Enhanced stop loss level using Fibonacci
4. Take profit targets using Fibonacci levels
5. Brief analysis of the breakout quality

Respond in JSON format:
{
  "symbol": "%s",
  "action": "LONG|SHORT|HOLD",
  "confidence": 85,
  "current_price": %.4f,
  "stop_loss": %.4f,
  "take_profit": %.4f,
  "analysis": "Your analysis here"
}`,
		breakoutSignal.Symbol,
		breakoutSignal.Symbol,
		breakoutSignal.CurrentPrice,
		breakoutSignal.BreakoutType,
		breakoutSignal.Signal,
		breakoutSignal.SupportLevel,
		breakoutSignal.ResistanceLevel,
		breakoutSignal.StopLoss,
		breakoutSignal.Confidence,
		breakoutSignal.PreviousCandle.Open,
		breakoutSignal.PreviousCandle.High,
		breakoutSignal.PreviousCandle.Low,
		breakoutSignal.PreviousCandle.Close,
		getCandleColor(breakoutSignal.PreviousCandle),
		breakoutSignal.CurrentCandle.Open,
		breakoutSignal.CurrentCandle.High,
		breakoutSignal.CurrentCandle.Low,
		breakoutSignal.CurrentCandle.Close,
		getCandleColor(breakoutSignal.CurrentCandle),
		fibonacci.High,
		fibonacci.Low,
		fibonacci.Level236,
		fibonacci.Level382,
		fibonacci.Level500,
		fibonacci.Level618,
		fibonacci.Level786,
		fibonacci.Direction,
		breakoutSignal.Analysis,
		breakoutSignal.Symbol,
		breakoutSignal.CurrentPrice,
		breakoutSignal.StopLoss,
		breakoutSignal.TakeProfit,
	)

	// Call AI API
	response, err := callAIAPI(prompt)
	if err != nil {
		return nil, err
	}

	// Parse AI response
	var aiSignal TradingSignal
	if err := json.Unmarshal([]byte(response), &aiSignal); err != nil {
		return nil, fmt.Errorf("failed to parse AI response: %v", err)
	}

	// Validate AI response
	if aiSignal.Action != "LONG" && aiSignal.Action != "SHORT" && aiSignal.Action != "HOLD" {
		return nil, fmt.Errorf("invalid AI action: %s", aiSignal.Action)
	}

	if aiSignal.Confidence < 60 {
		return nil, fmt.Errorf("AI confidence too low: %d%%", aiSignal.Confidence)
	}

	return &aiSignal, nil
}

// callAIAPI calls the AI API with the given prompt
func callAIAPI(prompt string) (string, error) {
	err := godotenv.Load()
	if err != nil {
		return "", fmt.Errorf("error loading .env file: %v", err)
	}

	apiKey := os.Getenv("DEEPSEEK_API_KEY")
	if apiKey == "" {
		return "", fmt.Errorf("DEEPSEEK_API_KEY not found in environment variables")
	}

	// Create request
	request := DeepSeekRequest{
		Model: "deepseek-chat",
		Messages: []Message{
			{
				Role:    "user",
				Content: prompt,
			},
		},
		Temperature: 0.3,
		MaxTokens:   1000,
	}

	jsonData, err := json.Marshal(request)
	if err != nil {
		return "", fmt.Errorf("failed to marshal request: %v", err)
	}

	// Make API call
	req, err := http.NewRequest("POST", "https://api.deepseek.com/v1/chat/completions", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("failed to create request: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("failed to make API call: %v", err)
	}
	defer resp.Body.Close()

	// Parse response
	var apiResp DeepSeekResponse
	if err := json.NewDecoder(resp.Body).Decode(&apiResp); err != nil {
		return "", fmt.Errorf("failed to parse response: %v", err)
	}

	if apiResp.Error.Message != "" {
		return "", fmt.Errorf("API error: %s", apiResp.Error.Message)
	}

	if len(apiResp.Choices) == 0 {
		return "", fmt.Errorf("no response from AI")
	}

	return apiResp.Choices[0].Message.Content, nil
}

// calculateFibonacci calculates Fibonacci levels from price data
func calculateFibonacci(candleData []*CandleData) *FibonacciLevels {
	if len(candleData) < 20 {
		return &FibonacciLevels{}
	}

	// Find the highest high and lowest low in recent data
	var high, low float64
	period := 50
	if len(candleData) < period {
		period = len(candleData)
	}

	recentData := candleData[len(candleData)-period:]
	high = recentData[0].High
	low = recentData[0].Low

	for _, candle := range recentData {
		if candle.High > high {
			high = candle.High
		}
		if candle.Low < low {
			low = candle.Low
		}
	}

	// Calculate Fibonacci levels
	diff := high - low
	direction := "UP"
	if recentData[len(recentData)-1].Close < recentData[0].Close {
		direction = "DOWN"
	}

	return &FibonacciLevels{
		High:      high,
		Low:       low,
		Level236:  high - (diff * 0.236),
		Level382:  high - (diff * 0.382),
		Level500:  high - (diff * 0.500),
		Level618:  high - (diff * 0.618),
		Level786:  high - (diff * 0.786),
		Direction: direction,
	}
}

// getCandleColor returns the color of a candle (green/red)
func getCandleColor(candle *CandleData) string {
	if candle.Close > candle.Open {
		return "Green"
	}
	return "Red"
}

// Helper functions for quantity and price formatting
func formatQuantity(symbol string, quantity float64) float64 {
	// Simple rounding for most pairs
	return math.Round(quantity*1000) / 1000
}

func formatQuantityString(symbol string, quantity float64) string {
	return fmt.Sprintf("%.3f", quantity)
}

// placeOrderWithRetry tries to place an order with multiple retry attempts
func placeOrderWithRetry(ctx context.Context, tradingClient *trading.TradingClient, symbol string, side futures.SideType, quantity float64) (*futures.CreateOrderResponse, error) {
	var lastErr error
	
	// Method 1: Direct quantity
	quantityStr := fmt.Sprintf("%.6f", quantity)
	order, err := tradingClient.BinanceClient.NewCreateOrderService().
		Symbol(symbol).
		Side(side).
		Type("MARKET").
		Quantity(quantityStr).
		Do(ctx)
	if err == nil {
		return order, nil
	}
	lastErr = err
	
	// Method 2: Try with smaller quantity
	smallerQuantity := quantity * 0.9
	quantityStr = fmt.Sprintf("%.3f", smallerQuantity)
	order, err = tradingClient.BinanceClient.NewCreateOrderService().
		Symbol(symbol).
		Side(side).
		Type("MARKET").
		Quantity(quantityStr).
		Do(ctx)
	if err == nil {
		return order, nil
	}
	lastErr = err
	
	return nil, fmt.Errorf("all order placement methods failed, last error: %w", lastErr)
}

// StartTrading starts the breakout trading system
func StartTrading() {
	// Load configuration
	_, err := config.LoadConfig("config.json")
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Initialize trading client
	tradingClient, err := trading.NewTradingClient()
	if err != nil {
		log.Fatalf("Failed to create trading client: %v", err)
	}

	// Get symbols for trading - using predefined list for now
	symbols := []string{
		"BTCUSDT", "ETHUSDT", "ADAUSDT", "XRPUSDT", "DOTUSDT",
		"LINKUSDT", "LTCUSDT", "BCHUSDT", "XLMUSDT", "UNIUSDT",
		"AAVEUSDT", "SUSHIUSDT", "SNXUSDT", "CRVUSDT", "YFIUSDT",
		"1INCHUSDT", "COMPUSDT", "MKRUSDT", "RENUSDT", "KNCUSDT",
	}

	// Start breakout trading
	startBreakoutTrading(tradingClient, symbols)
}
