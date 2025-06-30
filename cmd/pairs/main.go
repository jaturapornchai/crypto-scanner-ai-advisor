package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"tread2/pkg/trading"
)

func main() {
	fmt.Println("🪙 Binance Futures USDT Pairs Viewer")
	fmt.Println("====================================")

	// Check for command line argument
	showAll := false
	if len(os.Args) > 1 && os.Args[1] == "--all" {
		showAll = true
	}

	// Initialize client
	ctx := context.Background()
	client, err := trading.NewTradingClient()
	if err != nil {
		log.Fatalf("❌ Failed to initialize client: %v", err)
	}

	fmt.Println("🔗 Connecting to Binance Futures...")

	// Display USDT pairs
	if err := client.DisplayUSDTPairs(ctx, showAll); err != nil {
		log.Fatalf("❌ Failed to get USDT pairs: %v", err)
	}

	if !showAll {
		fmt.Println("💡 Use '--all' flag to see all USDT pairs:")
		fmt.Println("   go run cmd/pairs/main.go --all")
	}

	fmt.Println("\n✅ Data retrieved successfully!")
}
