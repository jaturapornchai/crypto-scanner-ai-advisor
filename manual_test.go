package main

import (
	"fmt"
	"log"
	"time"

	config "tread2/internal"
	"tread2/pkg/trading"
)

func main() {
	fmt.Println("🧪 MANUAL SCAN TEST")
	fmt.Println("==================")
	
	// Load configuration
	_, err := config.LoadConfig("config.json")
	if err != nil {
		log.Printf("Warning: Failed to load config: %v", err)
	}

	// Initialize trading client
	tradingClient, err := trading.NewTradingClient()
	if err != nil {
		log.Printf("Error: Failed to create trading client: %v", err)
		fmt.Println("📝 Note: This requires valid Binance API credentials.")
		return
	}

	// Test symbols
	symbols := []string{"BTCUSDT", "ETHUSDT"}

	fmt.Printf("🔍 Manual scan for %d symbols...\n", len(symbols))
	fmt.Printf("⏰ Scan time: %s\n", time.Now().Format("15:04:05"))

	// Run manual scan
	signals, err := scanForBreakouts(tradingClient, symbols)
	if err != nil {
		log.Printf("Scan error: %v", err)
		return
	}

	fmt.Printf("✅ Scan complete: %d signals found\n", len(signals))
	if len(signals) == 0 {
		fmt.Println("⚪ No breakout signals detected")
	}
}
