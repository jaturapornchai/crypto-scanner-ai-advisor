package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"tread2/pkg/trading"
)

func main() {
	fmt.Println("🚀 Binance Futures Balance Checker")
	fmt.Println("===================================")

	// Check environment variables
	if !checkEnvironment() {
		return
	}

	// Initialize client
	ctx := context.Background()
	client, err := trading.NewTradingClient()
	if err != nil {
		log.Fatalf("❌ Failed to initialize client: %v", err)
	}

	// Test connection and get balance
	fmt.Println("🔗 Connecting to Binance Futures...")

	if err := client.DisplayAccountSummary(ctx); err != nil {
		fmt.Printf("❌ Connection failed: %v\n", err)

		// Provide helpful error messages
		if containsAny(err.Error(), []string{"Invalid API-key", "API-key"}) {
			fmt.Println("\n💡 Possible solutions:")
			fmt.Println("   • Check your API key is correct")
			fmt.Println("   • Ensure Futures trading is enabled on your account")
			fmt.Println("   • Verify IP restrictions (if enabled)")
			fmt.Println("   • Make sure you're using testnet credentials for testnet")
		}
		return
	}

	// Get tradable balance
	balance, err := client.GetTradableBalance(ctx)
	if err != nil {
		fmt.Printf("⚠️  Could not get tradable balance: %v\n", err)
	} else {
		fmt.Printf("\n🎯 Final Result: %.4f USDT available for trading\n", balance)
	}
}

func checkEnvironment() bool {
	apiKey := os.Getenv("BINANCE_API_KEY")
	secretKey := os.Getenv("BINANCE_SECRET_KEY")

	if apiKey == "" {
		fmt.Println("❌ BINANCE_API_KEY not found in environment")
		showEnvHelp()
		return false
	}

	if secretKey == "" {
		fmt.Println("❌ BINANCE_SECRET_KEY not found in environment")
		showEnvHelp()
		return false
	}

	fmt.Printf("✅ API Key: %s...%s\n", apiKey[:8], apiKey[len(apiKey)-8:])
	fmt.Printf("✅ Secret Key: %s...%s\n", secretKey[:8], secretKey[len(secretKey)-8:])

	testnet := os.Getenv("USE_TESTNET")
	if testnet == "true" {
		fmt.Println("🧪 Using TESTNET environment")
	} else {
		fmt.Println("🚀 Using LIVE environment")
	}

	return true
}

func showEnvHelp() {
	fmt.Println("\n📝 Create a .env file with:")
	fmt.Println("BINANCE_API_KEY=your_api_key_here")
	fmt.Println("BINANCE_SECRET_KEY=your_secret_key_here")
	fmt.Println("USE_TESTNET=true")
	fmt.Println("\nOr set environment variables directly.")
}

func containsAny(s string, substrs []string) bool {
	for _, substr := range substrs {
		if len(s) >= len(substr) {
			for i := 0; i <= len(s)-len(substr); i++ {
				if s[i:i+len(substr)] == substr {
					return true
				}
			}
		}
	}
	return false
}
