package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"math/rand"
	"net/http"
	"os"
	"sort"
	"strings"
	"time"

	config "tread2/internal"
	"tread2/pkg/analysis"
	"tread2/pkg/trading"
	"tread2/pkg/utils"

	"github.com/joho/godotenv"
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

func runTrader() {
	// Load configuration
	appConfig, err := config.LoadConfig("config.json")
	if err != nil {
		log.Printf("Warning: Could not load config: %v. Using defaults.", err)
		appConfig = config.DefaultConfig()
	}

	fmt.Printf("Starting %s\n", appConfig.String())
	fmt.Println("Welcome to Tread2 Go Project!")

	// Example: String utilities
	stringHelper := utils.NewStringHelper()
	greeting := greetUser("Developer")
	fmt.Println(greeting)
	fmt.Println("Capitalized:", stringHelper.Capitalize("hello world"))
	fmt.Println("Reversed:", stringHelper.Reverse("golang"))
	fmt.Println("Is 'racecar' a palindrome?", stringHelper.IsPalindrome("racecar"))

	// Example: Math utilities with error handling
	mathHelper := utils.NewMathHelper()
	result, err := mathHelper.Divide(10, 2)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("10 / 2 = %.2f\n", result)

	// Example: Time utilities
	timeHelper := utils.NewTimeHelper()
	fmt.Printf("Current time: %s\n", timeHelper.FormatDateTime(time.Now()))

	if appConfig.Debug {
		fmt.Println("Debug mode is enabled")
	}

	// Binance Futures Trading
	fmt.Println("\n" + strings.Repeat("=", 50))
	fmt.Println("🚀 Initializing Binance Futures Trading Client...")

	ctx := context.Background()
	tradingClient, err := trading.NewTradingClient()
	if err != nil {
		log.Fatalf("Failed to initialize trading client: %v", err)
	}

	// Display account summary
	if err := tradingClient.DisplayAccountSummary(ctx); err != nil {
		log.Fatalf("Failed to display account summary: %v", err)
	}

	// Get specific tradable balance
	tradableBalance, err := tradingClient.GetTradableBalance(ctx)
	if err != nil {
		log.Printf("Failed to get tradable balance: %v", err)
	} else {
		fmt.Printf("\n✅ Ready to trade with: %.4f USDT\n", tradableBalance)
	}

	// Start Full Market Scanner
startTrading:
	// Cleanup orphaned orders before scanning (moved inside loop)
	fmt.Println("\n" + strings.Repeat("=", 60))
	fmt.Println("🧹 Pre-Scan Cleanup")
	fmt.Println("====================")

	if err := tradingClient.CleanupOrphaneOrders(ctx); err != nil {
		log.Printf("⚠️  Warning: Failed to cleanup orphaned orders: %v", err)
	}
	fmt.Println("\n" + strings.Repeat("=", 60))
	fmt.Println("🔍 Multi-Symbol Breakout Scanner - All USDT Pairs")
	fmt.Println("================================================")
	fmt.Println("📊 Scanning ALL USDT pairs for breakout patterns...")
	fmt.Println()

	// Get all USDT pairs from exchange
	fmt.Println("🔄 Fetching all USDT pairs from Binance...")
	allPairs, err := tradingClient.GetUSDTPairs(ctx)
	if err != nil {
		log.Fatalf("❌ Failed to get USDT pairs: %v", err)
	}

	// Shuffle the pairs for random scanning order
	rand.Seed(time.Now().UnixNano())
	rand.Shuffle(len(allPairs), func(i, j int) {
		allPairs[i], allPairs[j] = allPairs[j], allPairs[i]
	})

	// Initialize technical analyzer
	analyzer := analysis.NewTechnicalAnalyzer()

	// Scan all symbols sequentially (one by one)
	fmt.Printf("🚀 Scanning %d USDT pairs (randomized order) - Sequential Mode...\n", len(allPairs))
	fmt.Println("📝 Processing one symbol at a time...")
	fmt.Println()
	startTime := time.Now()

	var allSignals []*analysis.BreakoutSignal
	errorCount := 0
	processedCount := 0

	// Sequential scanning - one symbol at a time
	for i, symbol := range allPairs {
		processedCount++

		// Show progress
		fmt.Printf("📊 [%d/%d] Scanning %s...", i+1, len(allPairs), symbol.Symbol)

		signals, err := analyzer.AnalyzeSymbol(tradingClient.BinanceClient, symbol.Symbol)

		if err != nil {
			errorCount++
			fmt.Printf(" ❌ Error: %v\n", err)
			// If too many errors, show warning
			if errorCount > 10 {
				fmt.Printf("⚠️  Too many errors (%d), continuing with remaining symbols...\n", errorCount)
			}
			// Longer delay after error
			time.Sleep(200 * time.Millisecond)
			continue
		}

		if len(signals) > 0 {
			fmt.Printf(" ✅ Found %d signals\n", len(signals))
			for _, signal := range signals {
				signal.Symbol = symbol.Symbol // Ensure symbol is set
				allSignals = append(allSignals, signal)
			}
		} else {
			fmt.Printf(" ⚪ No signals\n")
		}

		// Rate limiting delay
		time.Sleep(100 * time.Millisecond)

		// Progress checkpoint every 50 symbols
		if (i+1)%50 == 0 {
			fmt.Printf("\n🔄 Progress checkpoint: %d/%d symbols scanned\n", i+1, len(allPairs))
			if len(allSignals) > 0 {
				fmt.Printf("   📊 Found %d signals so far\n", len(allSignals))
			}
			fmt.Println()
		}
	}

	duration := time.Since(startTime)

	fmt.Printf("\n⏱️  Scan completed in %.2f seconds\n", duration.Seconds())
	fmt.Printf("📊 Processed: %d/%d symbols\n", processedCount-errorCount, len(allPairs))
	if errorCount > 0 {
		fmt.Printf("❌ Errors: %d\n", errorCount)
	}

	// Display all signals
	if len(allSignals) > 0 {
		fmt.Printf("\n🎯 BREAKOUT SIGNALS SUMMARY (%d total)\n", len(allSignals))
		fmt.Println(strings.Repeat("=", 50))

		result := analyzer.FormatSignals(allSignals)
		fmt.Println(result)

		// Display comprehensive summary
		displayComprehensiveSummary(allSignals)

		// Show breakout summary by symbols
		showBreakoutSymbolsSummary(allSignals)

		// Show top opportunities
		showTopOpportunities(allSignals)

		// AI Analysis for successful retest symbols only
		fmt.Println("\n" + strings.Repeat("=", 60))
		fmt.Println("🤖 AI TRADING ANALYSIS - Successful Retest Coins Only")
		fmt.Println("====================================================")

		// Get unique symbols with RETEST_SUCCESS signals only
		retestSuccessSymbols := make(map[string]bool)
		for _, signal := range allSignals {
			if signal.Type == "RETEST_SUCCESS" {
				retestSuccessSymbols[signal.Symbol] = true
			}
		}

		if len(retestSuccessSymbols) == 0 {
			fmt.Println("❌ No symbols with successful retest found. Skipping AI analysis.")
		} else {
			fmt.Printf("🎯 Found %d symbols with successful retest. Analyzing with AI...\n\n", len(retestSuccessSymbols))

			// Analyze each symbol with AI
			aiAnalysisCount := 0
			for symbol := range retestSuccessSymbols {
				aiAnalysisCount++
				fmt.Printf("🔍 [%d/%d] AI Analysis for %s...\n", aiAnalysisCount, len(retestSuccessSymbols), symbol)

				// Get candlestick data for AI analysis
				candleData, err := getCandlestickData(tradingClient, symbol, 200)
				if err != nil {
					fmt.Printf("❌ Failed to get candle data for %s: %v\n", symbol, err)
					continue
				}

				// Send to AI for analysis
				aiSignal, err := analyzeWithAI(symbol, candleData)
				if err != nil {
					fmt.Printf("❌ AI analysis failed for %s: %v\n", symbol, err)
					continue
				}

				// Display AI recommendation
				displayAIRecommendation(aiSignal)

				// Check confidence threshold (≥80%) and open position
				if (aiSignal.Action == "LONG" || aiSignal.Action == "SHORT") && aiSignal.Confidence >= 85 {
					fmt.Printf("✅ Confidence ≥85%% - Proceeding with trade\n")
					err := openRealPosition(tradingClient, aiSignal)
					if err != nil {
						fmt.Printf("❌ Failed to open position for %s: %v\n", symbol, err)
						fmt.Printf("⏰ Error detected! Stopping current cycle and waiting for next round...\n")
						fmt.Printf("🕐 Current time: %s\n", time.Now().Format("2006-01-02 15:04:05"))
						fmt.Printf("🕑 Next cycle at: %s\n", time.Now().Add(1*time.Hour).Format("2006-01-02 15:04:05"))

						// Wait for 1 hour
						time.Sleep(1 * time.Hour)

						fmt.Printf("\n🔄 RESUMING TRADING CYCLE...\n")
						fmt.Printf("🕐 Current time: %s\n", time.Now().Format("2006-01-02 15:04:05"))

						// Restart the entire trading process
						fmt.Println("\n🚀 RESTARTING CRYPTO TRADING SCANNER...")
						goto startTrading
					}
				} else if aiSignal.Action == "LONG" || aiSignal.Action == "SHORT" {
					fmt.Printf("⚠️ Confidence %d%% < 85%% - Skipping trade (waiting for better opportunity)\n", aiSignal.Confidence)
				} else {
					fmt.Printf("⏸️ AI recommends HOLD - No trade action\n")
				}

				// Delay between AI calls
				time.Sleep(2 * time.Second)
			}
		}
	}

	fmt.Println("\n📊 No breakout signals detected across all scanned symbols")
	fmt.Println("💡 This could indicate:")
	fmt.Println("   • Market is in consolidation phase")
	fmt.Println("   • No clear trends in the scanned timeframe")
	fmt.Println("   • Wait for better setups to develop")
}

// greetUser returns a personalized greeting
func greetUser(name string) string {
	return fmt.Sprintf("Hello, %s! Ready to code in Go?", name)
}

// displayComprehensiveSummary shows comprehensive analysis of all signals
func displayComprehensiveSummary(signals []*analysis.BreakoutSignal) {
	symbolCount := make(map[string]int)
	typeCount := make(map[string]int)
	totalConfidence := 0.0
	highConfidenceSignals := 0

	for _, signal := range signals {
		symbolCount[signal.Symbol]++
		typeCount[signal.Type]++
		totalConfidence += signal.Confidence

		if signal.Confidence >= 0.85 {
			highConfidenceSignals++
		}
	}

	avgConfidence := totalConfidence / float64(len(signals))

	fmt.Println("📈 COMPREHENSIVE ANALYSIS:")
	fmt.Printf("   🎯 Total Signals: %d\n", len(signals))
	fmt.Printf("   📊 Average Confidence: %.1f%%\n", avgConfidence*100)
	fmt.Printf("   🔥 High Confidence (≥85%%): %d signals\n", highConfidenceSignals)
	fmt.Printf("   📈 Up Breakouts: %d\n", typeCount["UP_BREAKOUT"])
	fmt.Printf("   📉 Down Breakouts: %d\n", typeCount["DOWN_BREAKOUT"])
	fmt.Printf("   ✅ Successful Retests: %d\n", typeCount["RETEST_SUCCESS"])
	fmt.Printf("   ❌ Failed Retests: %d\n", typeCount["RETEST_FAILED"])

	// Market sentiment
	upBreakouts := float64(typeCount["UP_BREAKOUT"])
	downBreakouts := float64(typeCount["DOWN_BREAKOUT"])

	fmt.Printf("\n🌡️  MARKET SENTIMENT: ")
	if upBreakouts > downBreakouts*1.5 {
		fmt.Println("STRONG BULLISH 🚀")
	} else if upBreakouts > downBreakouts {
		fmt.Println("BULLISH 📈")
	} else if downBreakouts > upBreakouts*1.5 {
		fmt.Println("STRONG BEARISH 📉")
	} else if downBreakouts > upBreakouts {
		fmt.Println("BEARISH 📉")
	} else {
		fmt.Println("NEUTRAL ⚖️")
	}

	fmt.Println()
}

// showTopOpportunities displays top opportunities by confidence
func showTopOpportunities(signals []*analysis.BreakoutSignal) {
	if len(signals) == 0 {
		return
	}

	// Sort by confidence
	sortedSignals := make([]*analysis.BreakoutSignal, len(signals))
	copy(sortedSignals, signals)

	// Simple bubble sort by confidence (descending)
	for i := 0; i < len(sortedSignals)-1; i++ {
		for j := 0; j < len(sortedSignals)-i-1; j++ {
			if sortedSignals[j].Confidence < sortedSignals[j+1].Confidence {
				sortedSignals[j], sortedSignals[j+1] = sortedSignals[j+1], sortedSignals[j]
			}
		}
	}

	fmt.Println("🏆 TOP OPPORTUNITIES (by confidence):")
	fmt.Println(strings.Repeat("-", 40))

	count := 5
	if len(sortedSignals) < count {
		count = len(sortedSignals)
	}

	for i := 0; i < count; i++ {
		signal := sortedSignals[i]
		emoji := "📈"
		if signal.Type == "DOWN_BREAKOUT" {
			emoji = "📉"
		} else if signal.Type == "RETEST_SUCCESS" {
			emoji = "✅"
		} else if signal.Type == "RETEST_FAILED" {
			emoji = "❌"
		}

		fmt.Printf("%d. %s %s - %s (%.1f%% confidence)\n",
			i+1, emoji, signal.Symbol, signal.Type, signal.Confidence*100)
		fmt.Printf("   Price: %.4f | Time: %s\n",
			signal.Price, signal.Timestamp.Format("15:04:05"))
	}

	fmt.Println()
}

// showBreakoutSymbolsSummary displays symbols categorized by breakout types
func showBreakoutSymbolsSummary(signals []*analysis.BreakoutSignal) {
	if len(signals) == 0 {
		return
	}

	// Categorize symbols by breakout type
	upBreakoutSymbols := make(map[string]bool)
	downBreakoutSymbols := make(map[string]bool)
	retestSuccessSymbols := make(map[string]bool)
	retestFailedSymbols := make(map[string]bool)

	for _, signal := range signals {
		switch signal.Type {
		case "UP_BREAKOUT":
			upBreakoutSymbols[signal.Symbol] = true
		case "DOWN_BREAKOUT":
			downBreakoutSymbols[signal.Symbol] = true
		case "RETEST_SUCCESS":
			retestSuccessSymbols[signal.Symbol] = true
		case "RETEST_FAILED":
			retestFailedSymbols[signal.Symbol] = true
		}
	}

	fmt.Printf("\n📋 BREAKOUT SYMBOLS SUMMARY:\n")
	fmt.Println(strings.Repeat("=", 50))

	// UP Breakouts
	if len(upBreakoutSymbols) > 0 {
		fmt.Printf("\n📈 UP BREAKOUT Symbols (%d):\n", len(upBreakoutSymbols))
		var upSymbols []string
		for symbol := range upBreakoutSymbols {
			upSymbols = append(upSymbols, symbol)
		}
		sort.Strings(upSymbols)

		for i, symbol := range upSymbols {
			if i > 0 && i%8 == 0 {
				fmt.Println()
			}
			fmt.Printf("%-12s ", symbol)
		}
		fmt.Println()
	}

	// DOWN Breakouts
	if len(downBreakoutSymbols) > 0 {
		fmt.Printf("\n📉 DOWN BREAKOUT Symbols (%d):\n", len(downBreakoutSymbols))
		var downSymbols []string
		for symbol := range downBreakoutSymbols {
			downSymbols = append(downSymbols, symbol)
		}
		sort.Strings(downSymbols)

		for i, symbol := range downSymbols {
			if i > 0 && i%8 == 0 {
				fmt.Println()
			}
			fmt.Printf("%-12s ", symbol)
		}
		fmt.Println()
	}

	// Successful Retests
	if len(retestSuccessSymbols) > 0 {
		fmt.Printf("\n✅ RETEST SUCCESS Symbols (%d):\n", len(retestSuccessSymbols))
		var retestSuccessList []string
		for symbol := range retestSuccessSymbols {
			retestSuccessList = append(retestSuccessList, symbol)
		}
		sort.Strings(retestSuccessList)

		for i, symbol := range retestSuccessList {
			if i > 0 && i%8 == 0 {
				fmt.Println()
			}
			fmt.Printf("%-12s ", symbol)
		}
		fmt.Println()
	}

	// Failed Retests
	if len(retestFailedSymbols) > 0 {
		fmt.Printf("\n❌ RETEST FAILED Symbols (%d):\n", len(retestFailedSymbols))
		var retestFailedList []string
		for symbol := range retestFailedSymbols {
			retestFailedList = append(retestFailedList, symbol)
		}
		sort.Strings(retestFailedList)

		for i, symbol := range retestFailedList {
			if i > 0 && i%8 == 0 {
				fmt.Println()
			}
			fmt.Printf("%-12s ", symbol)
		}
		fmt.Println()
	}

	// Summary statistics
	fmt.Printf("\n📊 QUICK STATS:\n")
	fmt.Printf("   📈 Symbols with UP breakouts: %d\n", len(upBreakoutSymbols))
	fmt.Printf("   📉 Symbols with DOWN breakouts: %d\n", len(downBreakoutSymbols))
	fmt.Printf("   ✅ Symbols with successful retests: %d\n", len(retestSuccessSymbols))
	fmt.Printf("   ❌ Symbols with failed retests: %d\n", len(retestFailedSymbols))

	// Adjust for overlaps (symbols might have multiple signal types)
	allSymbols := make(map[string]bool)
	for symbol := range upBreakoutSymbols {
		allSymbols[symbol] = true
	}
	for symbol := range downBreakoutSymbols {
		allSymbols[symbol] = true
	}
	for symbol := range retestSuccessSymbols {
		allSymbols[symbol] = true
	}
	for symbol := range retestFailedSymbols {
		allSymbols[symbol] = true
	}

	fmt.Printf("   🎯 Total unique symbols with signals: %d\n", len(allSymbols))
	fmt.Println()
}

// getCandlestickData retrieves 200 candlestick data points for AI analysis
func getCandlestickData(client *trading.TradingClient, symbol string, limit int) ([]CandleData, error) {
	klines, err := client.BinanceClient.NewKlinesService().
		Symbol(symbol).
		Interval("1h").
		Limit(limit).
		Do(context.Background())

	if err != nil {
		return nil, err
	}

	var candleData []CandleData
	for _, kline := range klines {
		open, _ := parseFloat(kline.Open)
		high, _ := parseFloat(kline.High)
		low, _ := parseFloat(kline.Low)
		close, _ := parseFloat(kline.Close)
		volume, _ := parseFloat(kline.Volume)

		candleData = append(candleData, CandleData{
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

// parseFloat safely converts string to float64
func parseFloat(s string) (float64, error) {
	if s == "" {
		return 0, nil
	}
	return parseFloat64(s)
}

// parseFloat64 is a helper function
func parseFloat64(s string) (float64, error) {
	var result float64
	_, err := fmt.Sscanf(s, "%f", &result)
	return result, err
}

// analyzeWithAI sends candlestick data to AI for analysis
func analyzeWithAI(symbol string, candleData []CandleData) (*TradingSignal, error) {
	// Load .env for AI API credentials
	err := godotenv.Load(".env")
	if err != nil {
		log.Printf("Warning: Could not load .env file: %v", err)
		// Continue without .env file, environment variables might be set directly
	}

	apiKey := os.Getenv("DEEPSEEK_API_KEY")
	baseURL := os.Getenv("AI_BASE_URL")
	if apiKey == "" || baseURL == "" {
		return nil, fmt.Errorf("missing DEEPSEEK_API_KEY or AI_BASE_URL in .env")
	}

	// Get current price
	currentPrice := candleData[len(candleData)-1].Close

	// Prepare market data summary for AI
	candleDataJSON, _ := json.Marshal(candleData)

	prompt := fmt.Sprintf(`คุณคือนักเทรด cryptocurrency ที่เก่งที่สุดในโลก 

วิเคราะห์ข้อมูลแท่งเทียน 200 periods ของ %s:

ข้อมูลแท่งเทียน (200 periods, 1h timeframe):
%s

กรุณาวิเคราะห์และตอบเฉพาะในรูปแบบ JSON ดังนี้:
{
    "action": "LONG|SHORT|HOLD",
    "confidence": 85,
    "stop_loss": 2350.50,
    "take_profit": 2580.75,
    "analysis": "สรุปการวิเคราะห์แบบสั้น"
}

หมายเหตุ:
- confidence: ความมั่นใจ 0-100 (เลขจำนวนเต็ม)
- ถ้าความมั่นใจต่ำกว่า 80 ให้ใช้ "HOLD"
- ให้ Stop Loss และ Take Profit เพียง 1 ระดับที่ดีที่สุดเท่านั้น`,
		symbol, string(candleDataJSON))

	// Prepare request
	reqBody := DeepSeekRequest{
		Model: "deepseek-chat",
		Messages: []Message{{
			Role:    "user",
			Content: prompt,
		}},
	}
	jsonData, _ := json.Marshal(reqBody)

	client := &http.Client{Timeout: 30 * time.Second}
	req, _ := http.NewRequest("POST", baseURL+"/chat/completions", bytes.NewBuffer(jsonData))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, _ := ioutil.ReadAll(resp.Body)

	var dsResp DeepSeekResponse
	if err := json.Unmarshal(body, &dsResp); err != nil {
		return nil, err
	}

	if len(dsResp.Choices) == 0 {
		return nil, fmt.Errorf("no response from AI")
	}

	// Parse AI response JSON
	aiContent := dsResp.Choices[0].Message.Content

	// Extract JSON from AI response
	startIdx := strings.Index(aiContent, "{")
	endIdx := strings.LastIndex(aiContent, "}") + 1

	if startIdx == -1 || endIdx == 0 {
		return nil, fmt.Errorf("invalid JSON response from AI")
	}

	jsonResponse := aiContent[startIdx:endIdx]

	// Parse the JSON response
	var aiSignal TradingSignal
	if err := json.Unmarshal([]byte(jsonResponse), &aiSignal); err != nil {
		return nil, fmt.Errorf("failed to parse AI JSON response: %v", err)
	}

	// Set additional fields
	aiSignal.Symbol = symbol
	aiSignal.CurrentPrice = currentPrice

	return &aiSignal, nil
}

// displayAIRecommendation shows the AI trading recommendation (simplified)
func displayAIRecommendation(signal *TradingSignal) {
	fmt.Printf("\n🤖 AI ANALYSIS: %s\n", signal.Symbol)
	fmt.Println(strings.Repeat("=", 40))

	actionEmoji := "⚡"
	if signal.Action == "LONG" {
		actionEmoji = "🚀"
	} else if signal.Action == "SHORT" {
		actionEmoji = "📉"
	} else if signal.Action == "HOLD" {
		actionEmoji = "⏸️"
	}

	fmt.Printf("%s Recommendation: %s\n", actionEmoji, signal.Action)
	fmt.Printf("🎯 Confidence: %d%%\n", signal.Confidence)

	if signal.Action != "HOLD" {
		fmt.Printf("� Take Profit: $%.4f\n", signal.TakeProfit)
		fmt.Printf("❌ Stop Loss: $%.4f\n", signal.StopLoss)
	}

	fmt.Printf("📈 Analysis: %s\n", signal.Analysis)
	fmt.Println()
}

// min returns the minimum of two integers
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// openRealPosition เปิด position จริงด้วย margin $15 (แบบเรียบง่าย)
func openRealPosition(client *trading.TradingClient, signal *TradingSignal) error {
	ctx := context.Background()

	// Calculate position size with $15 margin
	margin := 15.0
	leverage := 10.0
	positionValue := margin * leverage // $150 total position value
	quantity := positionValue / signal.CurrentPrice

	// Round to reasonable precision (3 decimal places)
	quantity = math.Floor(quantity*1000) / 1000

	fmt.Printf("\n� Opening Position: %s %s\n", signal.Action, signal.Symbol)
	fmt.Printf("💰 Margin: $%.0f | Quantity: %.3f\n", margin, quantity)

	// Set up leverage for the symbol
	if err := client.SetLeverage(signal.Symbol, int(leverage)); err != nil {
		fmt.Printf("⚠️ Leverage setup warning: %v\n", err)
	}

	// Create the market order
	side := "BUY"
	if signal.Action == "SHORT" {
		side = "SELL"
	}

	// Place the market order (error handling แบบใหม่)
	orderResponse, err := client.PlaceOrder(ctx, signal.Symbol, side, "MARKET", quantity, 0)
	if err != nil {
		// ถ้า error แสดงแล้วส่งกลับไป ไม่ต้อง panic
		fmt.Printf("❌ Order failed: %v\n", err)
		return err
	}

	fmt.Printf("✅ Position opened: %s (ID: %s)\n", signal.Symbol, orderResponse.OrderID)

	// Set Stop Loss and Take Profit orders
	stopSide := "SELL"
	if signal.Action == "SHORT" {
		stopSide = "BUY"
	}

	// Stop Loss
	if _, err := client.PlaceStopOrder(ctx, signal.Symbol, stopSide, quantity, signal.StopLoss); err != nil {
		fmt.Printf("⚠️ Stop Loss warning: %v\n", err)
	} else {
		fmt.Printf("✅ Stop Loss: $%.4f\n", signal.StopLoss)
	}

	// Take Profit
	if _, err := client.PlaceTakeProfitOrder(ctx, signal.Symbol, stopSide, quantity, signal.TakeProfit); err != nil {
		fmt.Printf("⚠️ Take Profit warning: %v\n", err)
	} else {
		fmt.Printf("✅ Take Profit: $%.4f\n", signal.TakeProfit)
	}

	return nil
}
