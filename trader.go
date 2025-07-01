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

// MeanReversionSignal represents mean reversion analysis
type MeanReversionSignal struct {
	Symbol         string  `json:"symbol"`
	CurrentPrice   float64 `json:"current_price"`
	MA50           float64 `json:"ma50"`
	MA200          float64 `json:"ma200"`
	BBUpper        float64 `json:"bb_upper"`
	BBMiddle       float64 `json:"bb_middle"`
	BBLower        float64 `json:"bb_lower"`
	BBWidth        float64 `json:"bb_width"`
	RSI            float64 `json:"rsi"`
	ZScore         float64 `json:"z_score"`          // Distance from mean in standard deviations
	Signal         string  `json:"signal"`           // OVERSOLD, OVERBOUGHT, NEUTRAL
	Strength       float64 `json:"strength"`         // Signal strength 0-100
	LinearRegPrice float64 `json:"linear_reg_price"` // Linear regression predicted price
	PriceDeviation float64 `json:"price_deviation"`  // % deviation from linear regression
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

		// Enhanced AI Analysis with Mean Reversion Strategy
		fmt.Println("\n" + strings.Repeat("=", 60))
		fmt.Println("🤖 ENHANCED AI + MEAN REVERSION ANALYSIS")
		fmt.Println("========================================")

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
			fmt.Printf("🎯 Found %d symbols with successful retest. Analyzing with Mean Reversion + AI...\n\n", len(retestSuccessSymbols))

			// Analyze each symbol with Mean Reversion + AI
			aiAnalysisCount := 0
			for symbol := range retestSuccessSymbols {
				aiAnalysisCount++
				fmt.Printf("🔍 [%d/%d] Enhanced Analysis for %s...\n", aiAnalysisCount, len(retestSuccessSymbols), symbol)

				// Get candlestick data for analysis
				candleData, err := getCandlestickData(tradingClient, symbol, 200)
				if err != nil {
					fmt.Printf("❌ Failed to get candle data for %s: %v\n", symbol, err)
					continue
				}

				// 1. Calculate Mean Reversion Signal
				meanRevSignal, err := calculateMeanReversion(candleData, symbol)
				if err != nil {
					fmt.Printf("❌ Mean reversion analysis failed for %s: %v\n", symbol, err)
					continue
				}

				// Display Mean Reversion Analysis
				displayMeanReversionAnalysis(meanRevSignal)

				// 2. Send to AI for analysis with enhanced prompt
				aiSignal, err := analyzeWithAIEnhanced(symbol, candleData, meanRevSignal)
				if err != nil {
					fmt.Printf("❌ AI analysis failed for %s: %v\n", symbol, err)
					continue
				}

				// Display AI recommendation
				displayAIRecommendation(aiSignal)

				// 3. Combined Strategy Decision
				finalDecision := combineMeanReversionAndAI(meanRevSignal, aiSignal)
				displayFinalDecision(finalDecision)

				// Check confidence threshold (≥60%) and open position
				if (finalDecision.Action == "LONG" || finalDecision.Action == "SHORT") && finalDecision.Confidence >= 60 {
					fmt.Printf("✅ Combined Confidence ≥60%% - Proceeding with trade\n")
					err := openRealPosition(tradingClient, finalDecision)
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
				} else if finalDecision.Action == "LONG" || finalDecision.Action == "SHORT" {
					fmt.Printf("⚠️ Combined Confidence %d%% < 60%% - Skipping trade (waiting for better opportunity)\n", finalDecision.Confidence)
				} else {
					fmt.Printf("⏸️ Strategy recommends HOLD - No trade action\n")
				}

				// Delay between analyses
				time.Sleep(3 * time.Second)
			}
		}
	}

	fmt.Println("\n📊 No breakout signals detected across all scanned symbols")
	fmt.Println("💡 This could indicate:")
	fmt.Println("   • Market is in consolidation phase")
	fmt.Println("   • No clear trends in the scanned timeframe")
	fmt.Println("   • Wait for better setups to develop")
}

// calculateMeanReversion analyzes mean reversion signals
func calculateMeanReversion(candles []CandleData, symbol string) (*MeanReversionSignal, error) {
	if len(candles) < 200 {
		return nil, fmt.Errorf("insufficient data for mean reversion analysis")
	}

	// Get prices for calculations
	prices := make([]float64, len(candles))
	for i, candle := range candles {
		prices[i] = candle.Close
	}

	currentPrice := prices[len(prices)-1]

	// Calculate Moving Averages
	ma50 := calculateMA(prices[len(prices)-50:], 50)
	ma200 := calculateMA(prices, 200)

	// Calculate Bollinger Bands (20 period, 2 standard deviations)
	bbUpper, bbMiddle, bbLower, bbWidth := calculateBollingerBands(prices[len(prices)-20:], 20, 2.0)

	// Calculate RSI (14 period)
	rsi := calculateRSI(prices[len(prices)-15:], 14)

	// Calculate Z-Score (price distance from MA in standard deviations)
	zScore := calculateZScore(currentPrice, ma50, prices[len(prices)-50:])

	// Calculate Linear Regression price
	linearRegPrice := calculateLinearRegression(prices[len(prices)-50:], 50)
	priceDeviation := ((currentPrice - linearRegPrice) / linearRegPrice) * 100

	// Determine signal
	signal := "NEUTRAL"
	strength := 0.0

	// Mean Reversion Logic
	if rsi < 30 && currentPrice < bbLower && zScore < -1.5 {
		signal = "OVERSOLD"
		strength = (30 - rsi) + ((bbLower - currentPrice) / bbLower * 100) + (math.Abs(zScore) * 20)
	} else if rsi > 70 && currentPrice > bbUpper && zScore > 1.5 {
		signal = "OVERBOUGHT"
		strength = (rsi - 70) + ((currentPrice - bbUpper) / bbUpper * 100) + (zScore * 20)
	}

	// Cap strength at 100
	if strength > 100 {
		strength = 100
	}

	return &MeanReversionSignal{
		Symbol:         symbol,
		CurrentPrice:   currentPrice,
		MA50:           ma50,
		MA200:          ma200,
		BBUpper:        bbUpper,
		BBMiddle:       bbMiddle,
		BBLower:        bbLower,
		BBWidth:        bbWidth,
		RSI:            rsi,
		ZScore:         zScore,
		Signal:         signal,
		Strength:       strength,
		LinearRegPrice: linearRegPrice,
		PriceDeviation: priceDeviation,
	}, nil
}

// calculateMA calculates simple moving average
func calculateMA(prices []float64, period int) float64 {
	if len(prices) < period {
		return 0
	}
	sum := 0.0
	for i := len(prices) - period; i < len(prices); i++ {
		sum += prices[i]
	}
	return sum / float64(period)
}

// calculateBollingerBands calculates Bollinger Bands
func calculateBollingerBands(prices []float64, period int, stdDev float64) (upper, middle, lower, width float64) {
	if len(prices) < period {
		return 0, 0, 0, 0
	}

	// Calculate SMA (middle band)
	middle = calculateMA(prices, period)

	// Calculate standard deviation
	variance := 0.0
	recentPrices := prices[len(prices)-period:]
	for _, price := range recentPrices {
		variance += math.Pow(price-middle, 2)
	}
	standardDeviation := math.Sqrt(variance / float64(period))

	// Calculate bands
	upper = middle + (standardDeviation * stdDev)
	lower = middle - (standardDeviation * stdDev)
	width = ((upper - lower) / middle) * 100

	return upper, middle, lower, width
}

// calculateRSI calculates Relative Strength Index
func calculateRSI(prices []float64, period int) float64 {
	if len(prices) < period+1 {
		return 50 // neutral RSI
	}

	gains := 0.0
	losses := 0.0

	// Calculate initial average gain and loss
	for i := 1; i <= period; i++ {
		change := prices[i] - prices[i-1]
		if change > 0 {
			gains += change
		} else {
			losses += math.Abs(change)
		}
	}

	avgGain := gains / float64(period)
	avgLoss := losses / float64(period)

	if avgLoss == 0 {
		return 100
	}

	rs := avgGain / avgLoss
	rsi := 100 - (100 / (1 + rs))

	return rsi
}

// calculateZScore calculates how many standard deviations price is from mean
func calculateZScore(currentPrice, mean float64, prices []float64) float64 {
	if len(prices) == 0 {
		return 0
	}

	// Calculate standard deviation
	variance := 0.0
	for _, price := range prices {
		variance += math.Pow(price-mean, 2)
	}
	stdDev := math.Sqrt(variance / float64(len(prices)))

	if stdDev == 0 {
		return 0
	}

	return (currentPrice - mean) / stdDev
}

// calculateLinearRegression calculates linear regression predicted price
func calculateLinearRegression(prices []float64, period int) float64 {
	if len(prices) < period {
		return prices[len(prices)-1]
	}

	n := float64(period)
	sumX := 0.0
	sumY := 0.0
	sumXY := 0.0
	sumX2 := 0.0

	recentPrices := prices[len(prices)-period:]

	for i, price := range recentPrices {
		x := float64(i)
		y := price
		sumX += x
		sumY += y
		sumXY += x * y
		sumX2 += x * x
	}

	// Calculate slope and intercept
	slope := (n*sumXY - sumX*sumY) / (n*sumX2 - sumX*sumX)
	intercept := (sumY - slope*sumX) / n

	// Predict next price (at position period)
	predictedPrice := slope*float64(period) + intercept

	return predictedPrice
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
- ถ้าความมั่นใจต่ำกว่า 60 ให้ใช้ "HOLD"
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

// displayMeanReversionAnalysis shows mean reversion analysis results
func displayMeanReversionAnalysis(signal *MeanReversionSignal) {
	fmt.Printf("\n📊 MEAN REVERSION ANALYSIS: %s\n", signal.Symbol)
	fmt.Println(strings.Repeat("=", 45))

	// Current status
	fmt.Printf("💰 Current Price: $%.4f\n", signal.CurrentPrice)
	fmt.Printf("📈 MA50: $%.4f | MA200: $%.4f\n", signal.MA50, signal.MA200)

	// Bollinger Bands
	fmt.Printf("📊 Bollinger Bands:\n")
	fmt.Printf("   Upper: $%.4f | Middle: $%.4f | Lower: $%.4f\n",
		signal.BBUpper, signal.BBMiddle, signal.BBLower)
	fmt.Printf("   Width: %.2f%%\n", signal.BBWidth)

	// Technical indicators
	fmt.Printf("⚡ RSI: %.1f", signal.RSI)
	if signal.RSI < 30 {
		fmt.Printf(" (OVERSOLD 🔴)")
	} else if signal.RSI > 70 {
		fmt.Printf(" (OVERBOUGHT 🟠)")
	} else {
		fmt.Printf(" (NEUTRAL 🟡)")
	}
	fmt.Println()

	// Z-Score analysis
	fmt.Printf("📏 Z-Score: %.2f", signal.ZScore)
	if signal.ZScore < -2 {
		fmt.Printf(" (EXTREME OVERSOLD 🔴)")
	} else if signal.ZScore < -1 {
		fmt.Printf(" (OVERSOLD 🟠)")
	} else if signal.ZScore > 2 {
		fmt.Printf(" (EXTREME OVERBOUGHT 🔴)")
	} else if signal.ZScore > 1 {
		fmt.Printf(" (OVERBOUGHT 🟠)")
	} else {
		fmt.Printf(" (NEUTRAL 🟡)")
	}
	fmt.Println()

	// Linear regression
	fmt.Printf("📈 Linear Regression Price: $%.4f (%.2f%% deviation)\n",
		signal.LinearRegPrice, signal.PriceDeviation)

	// Signal assessment
	signalEmoji := "⚪"
	if signal.Signal == "OVERSOLD" {
		signalEmoji = "🟢"
	} else if signal.Signal == "OVERBOUGHT" {
		signalEmoji = "🔴"
	}

	fmt.Printf("%s Mean Reversion Signal: %s (%.1f%% strength)\n",
		signalEmoji, signal.Signal, signal.Strength)
	fmt.Println()
}

// analyzeWithAIEnhanced sends candlestick data and mean reversion analysis to AI
func analyzeWithAIEnhanced(symbol string, candleData []CandleData, meanRevSignal *MeanReversionSignal) (*TradingSignal, error) {
	// Load .env for AI API credentials
	err := godotenv.Load(".env")
	if err != nil {
		log.Printf("Warning: Could not load .env file: %v", err)
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
	meanRevJSON, _ := json.Marshal(meanRevSignal)

	prompt := fmt.Sprintf(`คุณคือนักเทรด cryptocurrency ผู้เชี่ยวชาญด้าน Mean Reversion + AI Strategy

วิเคราะห์ข้อมูลสำหรับ %s:

ข้อมูลแท่งเทียน (200 periods, 1h timeframe):
%s

การวิเคราะห์ Mean Reversion ที่คำนวณแล้ว:
%s

หลักการ Mean Reversion Strategy:
- เมื่อราคาออกห่างจาก mean มากๆ (Z-Score > 2 หรือ < -2) แนวโน้มจะกลับไปหา mean
- RSI < 30 + ราคาต่ำกว่า Bollinger Lower = สัญญาณ BUY
- RSI > 70 + ราคาสูงกว่า Bollinger Upper = สัญญาณ SELL
- Linear Regression ช่วยประเมินทิศทางและ fair value

กรุณาวิเคราะห์ร่วมกับ Mean Reversion Signal และตอบในรูปแบบ JSON:
{
    "action": "LONG|SHORT|HOLD",
    "confidence": 85,
    "stop_loss": 2350.50,
    "take_profit": 2580.75,
    "analysis": "การวิเคราะห์ที่รวม Mean Reversion + Technical Analysis"
}

หมายเหตุ:
- confidence: ความมั่นใจ 0-100 (เลขจำนวนเต็ม)
- ถ้าความมั่นใจต่ำกว่า 60 ให้ใช้ "HOLD"
- พิจารณา Mean Reversion Signal ร่วมกับ chart pattern
- ให้ Stop Loss และ Take Profit ตาม Fibonacci retracement`,
		symbol, string(candleDataJSON), string(meanRevJSON))

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

// combineMeanReversionAndAI combines mean reversion and AI signals
func combineMeanReversionAndAI(meanRevSignal *MeanReversionSignal, aiSignal *TradingSignal) *TradingSignal {
	// Create combined signal
	combinedSignal := &TradingSignal{
		Symbol:       meanRevSignal.Symbol,
		CurrentPrice: meanRevSignal.CurrentPrice,
		StopLoss:     aiSignal.StopLoss,
		TakeProfit:   aiSignal.TakeProfit,
	}

	// Calculate combined confidence
	meanRevConfidence := meanRevSignal.Strength
	aiConfidence := float64(aiSignal.Confidence)

	// Weighted combination (60% AI, 40% Mean Reversion)
	combinedConfidence := (aiConfidence * 0.6) + (meanRevConfidence * 0.4)

	// Strategy logic
	action := "HOLD"
	analysis := ""

	// Strong alignment check
	if meanRevSignal.Signal == "OVERSOLD" && aiSignal.Action == "LONG" {
		action = "LONG"
		analysis = fmt.Sprintf("STRONG BUY: Mean Reversion OVERSOLD (%.1f%%) + AI LONG (%.0f%%) = Aligned signals",
			meanRevSignal.Strength, aiConfidence)
		// Bonus for alignment
		combinedConfidence += 10
	} else if meanRevSignal.Signal == "OVERBOUGHT" && aiSignal.Action == "SHORT" {
		action = "SHORT"
		analysis = fmt.Sprintf("STRONG SELL: Mean Reversion OVERBOUGHT (%.1f%%) + AI SHORT (%.0f%%) = Aligned signals",
			meanRevSignal.Strength, aiConfidence)
		// Bonus for alignment
		combinedConfidence += 10
	} else if meanRevSignal.Signal != "NEUTRAL" && aiSignal.Action != "HOLD" {
		// Conflicting signals - be more conservative
		if aiConfidence >= 90 && meanRevSignal.Strength >= 70 {
			action = aiSignal.Action
			analysis = fmt.Sprintf("MODERATE: AI %s (%.0f%%) vs Mean Rev %s (%.1f%%) - Following stronger AI signal",
				aiSignal.Action, aiConfidence, meanRevSignal.Signal, meanRevSignal.Strength)
			combinedConfidence -= 15 // Penalty for conflict
		} else {
			action = "HOLD"
			analysis = fmt.Sprintf("CONFLICTING: AI %s vs Mean Rev %s - Waiting for better alignment",
				aiSignal.Action, meanRevSignal.Signal)
			combinedConfidence = 50 // Low confidence for conflicts
		}
	} else if aiSignal.Action != "HOLD" && meanRevSignal.Signal == "NEUTRAL" {
		// AI signal with neutral mean reversion
		if aiConfidence >= 60 {
			action = aiSignal.Action
			analysis = fmt.Sprintf("AI LEAD: %s signal (%.0f%%) with neutral mean reversion",
				aiSignal.Action, aiConfidence)
		} else {
			analysis = fmt.Sprintf("WEAK: AI %s (%.0f%%) but low confidence with neutral mean reversion",
				aiSignal.Action, aiConfidence)
		}
	} else {
		analysis = fmt.Sprintf("NEUTRAL: Both AI (%s, %.0f%%) and Mean Rev (%s, %.1f%%) suggest no action",
			aiSignal.Action, aiConfidence, meanRevSignal.Signal, meanRevSignal.Strength)
	}

	// Cap confidence at 100
	if combinedConfidence > 100 {
		combinedConfidence = 100
	}
	if combinedConfidence < 0 {
		combinedConfidence = 0
	}

	combinedSignal.Action = action
	combinedSignal.Confidence = int(combinedConfidence)
	combinedSignal.Analysis = analysis

	return combinedSignal
}

// displayFinalDecision shows the final trading decision
func displayFinalDecision(signal *TradingSignal) {
	fmt.Printf("\n🎯 FINAL TRADING DECISION: %s\n", signal.Symbol)
	fmt.Println(strings.Repeat("=", 50))

	actionEmoji := "⚡"
	if signal.Action == "LONG" {
		actionEmoji = "🚀"
	} else if signal.Action == "SHORT" {
		actionEmoji = "📉"
	} else if signal.Action == "HOLD" {
		actionEmoji = "⏸️"
	}

	fmt.Printf("%s Final Action: %s\n", actionEmoji, signal.Action)
	fmt.Printf("🎯 Combined Confidence: %d%%\n", signal.Confidence)

	if signal.Action != "HOLD" {
		fmt.Printf("💰 Current Price: $%.4f\n", signal.CurrentPrice)
		fmt.Printf("🎯 Take Profit: $%.4f\n", signal.TakeProfit)
		fmt.Printf("❌ Stop Loss: $%.4f\n", signal.StopLoss)
	}

	fmt.Printf("📈 Strategy Analysis: %s\n", signal.Analysis)

	// Confidence level assessment
	if signal.Confidence >= 80 {
		fmt.Printf("💪 Confidence Level: VERY HIGH - Strong trade setup\n")
	} else if signal.Confidence >= 70 {
		fmt.Printf("✅ Confidence Level: HIGH - Good trade setup\n")
	} else if signal.Confidence >= 60 {
		fmt.Printf("⚠️ Confidence Level: MEDIUM - Trade approved\n")
	} else {
		fmt.Printf("🛑 Confidence Level: LOW - Trade not recommended\n")
	}

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

	fmt.Printf("\n💼 Opening Position: %s %s\n", signal.Action, signal.Symbol)
	fmt.Printf("💰 Margin: $%.0f | Quantity: %.3f\n", margin, quantity)

	// Set up leverage for the symbol
	if err := client.SetLeverage(signal.Symbol, int(leverage)); err != nil {
		fmt.Printf("⚠️ Leverage setup warning: %v\n", err)
	}

	// Set margin mode to ISOLATED before opening position
	fmt.Printf("⚙️ Setting margin mode to ISOLATED for %s...\n", signal.Symbol)
	if err := client.ChangeMarginMode(signal.Symbol, "ISOLATED"); err != nil {
		fmt.Printf("⚠️ Margin mode setup warning: %v\n", err)
	} else {
		fmt.Printf("✅ Margin mode set to ISOLATED for %s\n", signal.Symbol)
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

// greetUser returns a personalized greeting
func greetUser(name string) string {
	return fmt.Sprintf("Hello, %s! Welcome to the trading bot.", name)
}
