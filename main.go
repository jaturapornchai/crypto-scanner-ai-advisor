package main

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	config "tread2/internal"
	"tread2/pkg/trading"
	"tread2/pkg/utils"
)

func main() {
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
}

// greetUser returns a personalized greeting
func greetUser(name string) string {
	return fmt.Sprintf("Hello, %s! Ready to code in Go?", name)
}
