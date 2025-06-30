package main

import (
	"context"
	"fmt"
	"log"
	"math/rand"
	"sort"
	"strings"
	"time"

	"tread2/pkg/analysis"
	"tread2/pkg/trading"
)

// Popular trading pairs for scanning (fallback if API fails)
var popularPairs = []string{
	"BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
	"ADAUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT", "LTCUSDT",
	"AVAXUSDT", "UNIUSDT", "BCHUSDT", "XLMUSDT", "VETUSDT",
	"MATICUSDT", "FILUSDT", "TRXUSDT", "ETCUSDT", "THETAUSDT",
}

func main() {
	fmt.Println("🔍 Multi-Symbol Breakout Scanner - All USDT Pairs")
	fmt.Println("================================================")
	fmt.Println("📊 Scanning ALL USDT pairs for breakout patterns...")
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

	// Shuffle the pairs for random scanning order
	rand.Seed(time.Now().UnixNano())
	rand.Shuffle(len(allPairs), func(i, j int) {
		allPairs[i], allPairs[j] = allPairs[j], allPairs[i]
	})

	// Limit to 20 random pairs for quick testing
	testPairs := 20
	if len(allPairs) > testPairs {
		allPairs = allPairs[:testPairs]
		fmt.Printf("🎲 Selected %d random pairs for testing\n", testPairs)
	}

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

		signals, err := analyzer.AnalyzeSymbol(client.BinanceClient, symbol.Symbol)

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
	} else {
		fmt.Println("\n📊 No breakout signals detected across all scanned symbols")
		fmt.Println("💡 This could indicate:")
		fmt.Println("   • Market is in consolidation phase")
		fmt.Println("   • No clear trends in the scanned timeframe")
		fmt.Println("   • Wait for better setups to develop")
	}
}

func displayComprehensiveSummary(signals []*analysis.BreakoutSignal) {
	symbolCount := make(map[string]int)
	typeCount := make(map[string]int)
	totalConfidence := 0.0
	highConfidenceSignals := 0

	for _, signal := range signals {
		symbolCount[signal.Symbol]++
		typeCount[signal.Type]++
		totalConfidence += signal.Confidence

		if signal.Confidence >= 0.7 {
			highConfidenceSignals++
		}
	}

	avgConfidence := totalConfidence / float64(len(signals))

	fmt.Println("📈 COMPREHENSIVE ANALYSIS:")
	fmt.Printf("   🎯 Total Signals: %d\n", len(signals))
	fmt.Printf("   📊 Average Confidence: %.1f%%\n", avgConfidence*100)
	fmt.Printf("   🔥 High Confidence (≥70%%): %d signals\n", highConfidenceSignals)
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
