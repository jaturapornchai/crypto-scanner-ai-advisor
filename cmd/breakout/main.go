package main

import (
	"fmt"
	"log"
	"os"
	"strings"

	"tread2/pkg/analysis"
	"tread2/pkg/trading"
)

func main() {
	fmt.Println("🎯 Binance Futures Breakout Scanner")
	fmt.Println("===================================")

	// Initialize trading client
	client, err := trading.NewTradingClient()
	if err != nil {
		log.Fatalf("❌ Failed to initialize trading client: %v", err)
	}

	// Initialize technical analyzer
	analyzer := analysis.NewTechnicalAnalyzer()

	// Get symbol from command line or use default
	symbol := "BTCUSDT"
	if len(os.Args) > 1 {
		symbol = strings.ToUpper(os.Args[1])
		if !strings.HasSuffix(symbol, "USDT") {
			symbol = symbol + "USDT"
		}
	}

	fmt.Printf("🔍 Analyzing %s for breakout patterns...\n", symbol)
	fmt.Println("📊 Using Linear Regression Channel (Length: 100, Deviation: 2.0)")
	fmt.Println("⏰ Timeframe: 1 Hour")
	fmt.Println("🔙 Looking back: 10 candles for breakout detection")
	fmt.Println()

	// Analyze the symbol
	signals, err := analyzer.AnalyzeSymbol(client.BinanceClient, symbol)
	if err != nil {
		log.Fatalf("❌ Failed to analyze %s: %v", symbol, err)
	}

	// Display results
	result := analyzer.FormatSignals(signals)
	fmt.Println(result)

	// Display summary
	displaySummary(signals)

	fmt.Println("💡 Usage examples:")
	fmt.Println("   go run cmd/breakout/main.go ETHUSDT")
	fmt.Println("   go run cmd/breakout/main.go SOLUSDT")
	fmt.Println("   go run cmd/breakout/main.go BNB  # Will auto-add USDT")
}

func displaySummary(signals []*analysis.BreakoutSignal) {
	if len(signals) == 0 {
		fmt.Println("📊 Summary: No breakout signals detected in the last 10 hours")
		return
	}

	upBreakouts := 0
	downBreakouts := 0
	retests := 0
	totalConfidence := 0.0

	for _, signal := range signals {
		switch signal.Type {
		case "UP_BREAKOUT":
			upBreakouts++
		case "DOWN_BREAKOUT":
			downBreakouts++
		case "RETEST_SUCCESS":
			retests++
		}
		totalConfidence += signal.Confidence
	}

	avgConfidence := totalConfidence / float64(len(signals))

	fmt.Println("📊 Summary:")
	fmt.Printf("   📈 Up Breakouts: %d\n", upBreakouts)
	fmt.Printf("   📉 Down Breakouts: %d\n", downBreakouts)
	fmt.Printf("   🔄 Successful Retests: %d\n", retests)
	fmt.Printf("   🎯 Average Confidence: %.1f%%\n", avgConfidence*100)

	// Trading suggestion
	if upBreakouts > downBreakouts {
		fmt.Println("   💹 Trend Bias: BULLISH")
	} else if downBreakouts > upBreakouts {
		fmt.Println("   💹 Trend Bias: BEARISH")
	} else {
		fmt.Println("   💹 Trend Bias: NEUTRAL")
	}

	fmt.Println()
}
