package main

import (
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

	fmt.Println("🔧 Testing Margin Mode Change: ISOLATED ↔ CROSSED")
	fmt.Println("=================================================")

	// Create trading client
	client, err := trading.NewTradingClient()
	if err != nil {
		log.Fatalf("Failed to create trading client: %v", err)
	}

	symbol := "BTCUSDT"
	fmt.Printf("📊 Testing with symbol: %s\n\n", symbol)

	// Test 1: Check current mode
	fmt.Println("1️⃣ Checking current margin mode...")
	currentMode, err := client.GetMarginMode(symbol)
	if err != nil {
		log.Fatalf("❌ Failed to get current margin mode: %v", err)
	}
	fmt.Printf("   Current margin mode: %s\n", currentMode)

	// Test 2: Change to opposite mode
	var targetMode string
	if currentMode == "ISOLATED" {
		targetMode = "CROSSED"
	} else {
		targetMode = "ISOLATED"
	}

	fmt.Printf("\n2️⃣ Changing margin mode to %s...\n", targetMode)
	err = client.ChangeMarginMode(symbol, targetMode)
	if err != nil {
		fmt.Printf("❌ Failed to change margin mode: %v\n", err)
	} else {
		fmt.Printf("✅ Successfully sent change request\n")
	}

	// Test 3: Verify change
	fmt.Println("\n3️⃣ Verifying change...")
	time.Sleep(2 * time.Second)

	newMode, err := client.GetMarginMode(symbol)
	if err != nil {
		log.Fatalf("❌ Failed to verify margin mode: %v", err)
	}
	fmt.Printf("   New margin mode: %s\n", newMode)

	if newMode == targetMode {
		fmt.Printf("✅ SUCCESS: Changed from %s to %s\n", currentMode, targetMode)
	} else {
		fmt.Printf("❌ FAILED: Expected %s but got %s\n", targetMode, newMode)
	}

	// Test 4: Change back to ISOLATED (for consistency)
	if targetMode == "CROSSED" {
		fmt.Println("\n4️⃣ Changing back to ISOLATED...")
		err = client.ChangeMarginMode(symbol, "ISOLATED")
		if err != nil {
			fmt.Printf("❌ Failed to change back: %v\n", err)
		} else {
			fmt.Printf("✅ Changed back to ISOLATED\n")
		}

		time.Sleep(2 * time.Second)
		finalMode, _ := client.GetMarginMode(symbol)
		fmt.Printf("   Final mode: %s\n", finalMode)
	}

	fmt.Println("\n🏁 All tests completed!")
}
