package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"tread2/pkg/trading"

	"github.com/joho/godotenv"
)

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: Could not load .env file: %v", err)
	}

	fmt.Println("🔧 Testing Margin Mode Change to ISOLATED")
	fmt.Println("========================================")

	// Create trading client
	client, err := trading.NewTradingClient()
	if err != nil {
		log.Fatalf("Failed to create trading client: %v", err)
	}

	ctx := context.Background()
	symbol := "BTCUSDT"

	fmt.Printf("📊 Testing with symbol: %s\n\n", symbol)

	// Step 1: Check current margin mode
	fmt.Println("1️⃣ Checking current margin mode...")
	currentMode, err := client.GetMarginMode(symbol)
	if err != nil {
		log.Fatalf("❌ Failed to get current margin mode: %v", err)
	}
	fmt.Printf("   Current margin mode: %s\n", currentMode)

	// Step 2: Change to ISOLATED
	fmt.Println("\n2️⃣ Changing margin mode to ISOLATED...")
	err = client.ChangeMarginMode(symbol, "ISOLATED")
	if err != nil {
		fmt.Printf("❌ Failed to change margin mode: %v\n", err)
		// Check if it's the "No need to change" error
		if err.Error() == "failed to change margin mode: <APIError> code=-4046, msg=No need to change margin type." {
			fmt.Printf("✅ Already in ISOLATED mode (no change needed)\n")
		} else {
			log.Fatalf("❌ Unexpected error: %v", err)
		}
	} else {
		fmt.Printf("✅ Successfully sent change request\n")
	}

	// Step 3: Wait and verify
	fmt.Println("\n3️⃣ Waiting 2 seconds and verifying...")
	time.Sleep(2 * time.Second)

	newMode, err := client.GetMarginMode(symbol)
	if err != nil {
		log.Fatalf("❌ Failed to verify margin mode: %v", err)
	}
	fmt.Printf("   New margin mode: %s\n", newMode)

	// Step 4: Test result
	fmt.Println("\n4️⃣ Test Result:")
	if newMode == "ISOLATED" {
		fmt.Printf("✅ SUCCESS: Margin mode is now ISOLATED\n")
	} else {
		fmt.Printf("⚠️  WARNING: Margin mode is still %s (not ISOLATED)\n", newMode)
		fmt.Printf("   This might indicate detection logic needs improvement\n")
	}

	// Step 5: Show account positions for verification
	fmt.Println("\n5️⃣ Checking position details...")
	positions, err := client.BinanceClient.NewGetPositionRiskService().Do(ctx)
	if err != nil {
		fmt.Printf("❌ Failed to get position details: %v\n", err)
		return
	}

	found := false
	for _, pos := range positions {
		if pos.Symbol == symbol {
			found = true
			fmt.Printf("   Symbol: %s\n", pos.Symbol)
			fmt.Printf("   MarginType field: '%s'\n", pos.MarginType)
			fmt.Printf("   MaxNotionalValue: '%s'\n", pos.MaxNotionalValue)
			fmt.Printf("   IsolatedMargin: '%s'\n", pos.IsolatedMargin)
			fmt.Printf("   PositionAmt: '%s'\n", pos.PositionAmt)

			// Analyze the data
			if pos.MarginType == "isolated" {
				fmt.Printf("✅ Position data confirms ISOLATED mode\n")
			} else if pos.MarginType == "cross" {
				fmt.Printf("⚠️  Position data shows CROSS mode\n")
			} else {
				fmt.Printf("❓ MarginType field value: '%s'\n", pos.MarginType)
			}
			break
		}
	}

	if !found {
		fmt.Printf("❌ No position data found for %s\n", symbol)
	}

	fmt.Println("\n🏁 Test completed!")
}
