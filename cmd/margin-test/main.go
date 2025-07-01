package main

import (
	"context"
	"log"
	"time"

	"tread2/pkg/trading"

	"github.com/joho/godotenv"
)

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	log.Println("🔍 Testing Margin Mode Change")

	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: Could not load .env file: %v", err)
	}

	// Create trading client
	client, err := trading.NewTradingClient()
	if err != nil {
		log.Fatalf("Failed to create trading client: %v", err)
	}

	symbol := "BTCUSDT"

	// Check current margin mode
	currentMode, err := client.GetMarginMode(symbol)
	if err != nil {
		log.Fatalf("Failed to get margin mode for %s: %v", symbol, err)
	}

	log.Printf("Current margin mode for %s: %s", symbol, currentMode)

	// Change to ISOLATED if not already
	if currentMode != "ISOLATED" {
		log.Printf("Changing margin mode to ISOLATED for %s...", symbol)

		if err := client.ChangeMarginMode(symbol, "ISOLATED"); err != nil {
			log.Fatalf("Failed to set margin mode to ISOLATED: %v", err)
		}

		log.Printf("✅ Change command sent successfully")

		// Wait a moment for the change to take effect
		time.Sleep(2 * time.Second)

		// Check again to confirm
		newMode, err := client.GetMarginMode(symbol)
		if err != nil {
			log.Fatalf("Failed to get updated margin mode: %v", err)
		}

		log.Printf("Updated margin mode for %s: %s", symbol, newMode)

		if newMode != "ISOLATED" {
			log.Printf("⚠️ Warning: Margin mode still shows as %s instead of ISOLATED", newMode)
			log.Printf("This may indicate an issue with the GetMarginMode function's detection logic")
		} else {
			log.Printf("✅ Successfully changed margin mode to ISOLATED")
		}
	} else {
		log.Printf("✅ Margin mode is already ISOLATED")
	}

	// Additional test: Try to directly query position info to verify margin type
	log.Printf("\n📊 Directly querying position info for %s...", symbol)

	// Check if BinanceClient is available
	if client.BinanceClient == nil {
		log.Fatalf("BinanceClient is nil")
	}

	positions, err := client.BinanceClient.NewGetPositionRiskService().Do(context.Background())
	if err != nil {
		log.Fatalf("Failed to get position info: %v", err)
	}

	for _, pos := range positions {
		if pos.Symbol == symbol {
			log.Printf("Symbol: %s", pos.Symbol)
			log.Printf("MarginType: %s", pos.MarginType)
			log.Printf("MaxNotionalValue: %s", pos.MaxNotionalValue)
			log.Printf("IsolatedMargin: %s", pos.IsolatedMargin)
			log.Printf("IsAutoAddMargin: %s", pos.IsAutoAddMargin)
			break
		}
	}
}
