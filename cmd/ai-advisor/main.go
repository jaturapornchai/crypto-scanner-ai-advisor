package main

import (
	"context"
	"fmt"
	"log"
	"math/rand"
	"strings"
	"time"

	"tread2/pkg/analysis"
	"tread2/pkg/trading"
)

func main() {
	fmt.Println("🤖 AI Trading Advisor - Breakout Analysis with Fibonacci Levels")
	fmt.Println("================================================================")
	fmt.Println("📊 Testing 20 random USDT pairs for breakout signals...")
	fmt.Println()

	// Initialize trading client
	client, err := trading.NewTradingClient()
	if err != nil {
		log.Fatalf("❌ Failed to initialize trading client: %v", err)
	}

	// Get all USDT pairs from exchange
	fmt.Println("🔄 Fetching all USDT pairs from Binance...")
	allPairs, err := client.GetUSDTPairs(context.Background())
	if err != nil {
		log.Fatalf("❌ Failed to get USDT pairs: %v", err)
	}

	// Shuffle and select 20 random pairs
	rand.Seed(time.Now().UnixNano())
	rand.Shuffle(len(allPairs), func(i, j int) {
		allPairs[i], allPairs[j] = allPairs[j], allPairs[i]
	})

	testPairs := 20
	if len(allPairs) > testPairs {
		allPairs = allPairs[:testPairs]
	}

	fmt.Printf("🎲 Selected %d random pairs for AI analysis\n\n", len(allPairs))

	// Initialize technical analyzer
	analyzer := analysis.NewTechnicalAnalyzer()

	// Track breakout coins for AI advice
	var breakoutCoins []BreakoutInfo

	// Scan selected pairs
	fmt.Println("🔍 Scanning for breakout signals...")
	for i, symbol := range allPairs {
		fmt.Printf("📊 [%d/%d] Scanning %s...", i+1, len(allPairs), symbol.Symbol)

		signals, err := analyzer.AnalyzeSymbol(client.BinanceClient, symbol.Symbol)
		if err != nil {
			fmt.Printf(" ❌ Error: %v\n", err)
			continue
		}

		// Check for breakout signals
		hasBreakout := false
		hasRetest := false
		var breakoutType string
		var latestPrice float64
		var confidence float64

		for _, signal := range signals {
			if signal.Type == "UP_BREAKOUT" || signal.Type == "DOWN_BREAKOUT" {
				hasBreakout = true
				breakoutType = signal.Type
				latestPrice = signal.Price
				confidence = signal.Confidence
			}
			if signal.Type == "RETEST_SUCCESS" || signal.Type == "RETEST_FAILED" {
				hasRetest = true
			}
		}

		if hasBreakout && hasRetest {
			fmt.Printf(" 🎯 BREAKOUT + RETEST DETECTED!\n")
			breakoutCoins = append(breakoutCoins, BreakoutInfo{
				Symbol:       symbol.Symbol,
				BreakoutType: breakoutType,
				Price:        latestPrice,
				Confidence:   confidence,
				Signals:      signals,
			})
		} else if hasBreakout {
			fmt.Printf(" 📈 Breakout only\n")
		} else {
			fmt.Printf(" ⚪ No signals\n")
		}

		time.Sleep(100 * time.Millisecond) // Rate limiting
	}

	fmt.Printf("\n🎯 Found %d coins with BREAKOUT + RETEST signals\n", len(breakoutCoins))
	fmt.Println(strings.Repeat("=", 60))

	// AI Analysis for each breakout coin
	if len(breakoutCoins) == 0 {
		fmt.Println("❌ No coins with breakout + retest signals found in this sample")
		fmt.Println("💡 Try running again for different random selection")
		return
	}

	for i, coin := range breakoutCoins {
		fmt.Printf("\n🤖 AI ANALYSIS #%d: %s\n", i+1, coin.Symbol)
		fmt.Println(strings.Repeat("=", 40))

		// Get detailed market data for AI analysis
		advice := generateTradingAdvice(coin, client, analyzer)
		fmt.Println(advice)

		if i < len(breakoutCoins)-1 {
			fmt.Println("\n" + strings.Repeat("-", 60))
		}
	}

	fmt.Println("\n🚨 DISCLAIMER: This is AI-generated analysis based on technical indicators.")
	fmt.Println("⚠️  Always do your own research and manage risk appropriately!")
}

type BreakoutInfo struct {
	Symbol       string
	BreakoutType string
	Price        float64
	Confidence   float64
	Signals      []*analysis.BreakoutSignal
}

func generateTradingAdvice(coin BreakoutInfo, client *trading.TradingClient, analyzer *analysis.TechnicalAnalyzer) string {
	// Get recent price data for Fibonacci analysis
	klines, err := analyzer.GetKlineData(client.BinanceClient, coin.Symbol, "1h", 100)
	if err != nil {
		return fmt.Sprintf("❌ Error getting market data for %s", coin.Symbol)
	}

	if len(klines) < 20 {
		return fmt.Sprintf("❌ Insufficient data for %s", coin.Symbol)
	}

	// Calculate Fibonacci levels
	fib := calculateFibonacciLevels(klines)
	currentPrice := klines[len(klines)-1].Close

	advice := fmt.Sprintf("💰 SYMBOL: %s\n", coin.Symbol)
	advice += fmt.Sprintf("💵 Current Price: $%.4f\n", currentPrice)
	advice += fmt.Sprintf("📊 Breakout Type: %s\n", coin.BreakoutType)
	advice += fmt.Sprintf("🎯 Confidence: %.1f%%\n\n", coin.Confidence*100)

	// Generate trading recommendation based on breakout type
	if coin.BreakoutType == "UP_BREAKOUT" {
		advice += "🚀 AI RECOMMENDATION: **LONG POSITION**\n"
		advice += "📈 Rationale: Bullish breakout above resistance with retest confirmation\n\n"

		advice += "📊 FIBONACCI TARGETS:\n"
		advice += fmt.Sprintf("🎯 Take Profit 1 (38.2%%): $%.4f\n", fib.Extension_382)
		advice += fmt.Sprintf("🎯 Take Profit 2 (61.8%%): $%.4f\n", fib.Extension_618)
		advice += fmt.Sprintf("🎯 Take Profit 3 (100%%):  $%.4f\n", fib.Extension_100)
		advice += fmt.Sprintf("🛑 Stop Loss (23.6%%):     $%.4f\n\n", fib.Retracement_236)

		advice += "⚡ STRATEGY:\n"
		advice += "• Enter: Market or on pullback to breakout level\n"
		advice += "• Risk/Reward: 1:2 to 1:3 ratio\n"
		advice += "• Position Size: 1-2% of portfolio\n"

	} else if coin.BreakoutType == "DOWN_BREAKOUT" {
		advice += "📉 AI RECOMMENDATION: **SHORT POSITION**\n"
		advice += "🔻 Rationale: Bearish breakdown below support with retest failure\n\n"

		advice += "📊 FIBONACCI TARGETS:\n"
		advice += fmt.Sprintf("🎯 Take Profit 1 (38.2%%): $%.4f\n", fib.Extension_382_Down)
		advice += fmt.Sprintf("🎯 Take Profit 2 (61.8%%): $%.4f\n", fib.Extension_618_Down)
		advice += fmt.Sprintf("🎯 Take Profit 3 (100%%):  $%.4f\n", fib.Extension_100_Down)
		advice += fmt.Sprintf("🛑 Stop Loss (23.6%%):     $%.4f\n\n", fib.Retracement_764)

		advice += "⚡ STRATEGY:\n"
		advice += "• Enter: Market or on bounce to breakdown level\n"
		advice += "• Risk/Reward: 1:2 to 1:3 ratio\n"
		advice += "• Position Size: 1-2% of portfolio\n"
	}

	// Add market context
	advice += "\n📋 ADDITIONAL ANALYSIS:\n"
	for _, signal := range coin.Signals {
		if signal.Type == "RETEST_SUCCESS" {
			advice += "✅ Retest successful - confirms trend strength\n"
		} else if signal.Type == "RETEST_FAILED" {
			advice += "❌ Retest failed - trend continuation likely\n"
		}
	}

	return advice
}

type FibonacciLevels struct {
	High               float64
	Low                float64
	Retracement_236    float64
	Retracement_382    float64
	Retracement_500    float64
	Retracement_618    float64
	Retracement_764    float64
	Extension_382      float64
	Extension_618      float64
	Extension_100      float64
	Extension_382_Down float64
	Extension_618_Down float64
	Extension_100_Down float64
}

func calculateFibonacciLevels(klines []*analysis.Kline) FibonacciLevels {
	// Get recent high and low (last 20 candles)
	lookback := 20
	if len(klines) < lookback {
		lookback = len(klines)
	}

	recentKlines := klines[len(klines)-lookback:]

	var high, low float64
	high = recentKlines[0].High
	low = recentKlines[0].Low

	for _, k := range recentKlines {
		if k.High > high {
			high = k.High
		}
		if k.Low < low {
			low = k.Low
		}
	}

	diff := high - low

	return FibonacciLevels{
		High:               high,
		Low:                low,
		Retracement_236:    high - (diff * 0.236),
		Retracement_382:    high - (diff * 0.382),
		Retracement_500:    high - (diff * 0.500),
		Retracement_618:    high - (diff * 0.618),
		Retracement_764:    high - (diff * 0.764),
		Extension_382:      high + (diff * 0.382),
		Extension_618:      high + (diff * 0.618),
		Extension_100:      high + (diff * 1.000),
		Extension_382_Down: low - (diff * 0.382),
		Extension_618_Down: low - (diff * 0.618),
		Extension_100_Down: low - (diff * 1.000),
	}
}
