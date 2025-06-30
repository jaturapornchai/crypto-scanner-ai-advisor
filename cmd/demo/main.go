package main

import (
	"context"
	"fmt"
	"log"
	"os"
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

	displayWelcome(appConfig)
	demonstrateUtilities()

	// Check if we should run trading demo
	if shouldRunTradingDemo() {
		runTradingDemo()
	} else {
		fmt.Println("\n⚠️  Skipping trading demo - set valid API credentials in .env file to test")
		displayTradingInstructions()
	}
}

func displayWelcome(appConfig *config.AppConfig) {
	fmt.Printf("Starting %s\n", appConfig.String())
	fmt.Println("Welcome to Tread2 Go Project!")

	if appConfig.Debug {
		fmt.Println("🐛 Debug mode is enabled")
	}
}

func demonstrateUtilities() {
	fmt.Println("\n" + strings.Repeat("=", 50))
	fmt.Println("🛠️  Demonstrating Utility Functions...")

	// Example: String utilities
	stringHelper := utils.NewStringHelper()
	greeting := greetUser("Developer")
	fmt.Println("\n📝 String Utils:")
	fmt.Printf("├─ Greeting: %s\n", greeting)
	fmt.Printf("├─ Capitalized: %s\n", stringHelper.Capitalize("hello world"))
	fmt.Printf("├─ Reversed: %s\n", stringHelper.Reverse("golang"))
	fmt.Printf("└─ Is 'racecar' a palindrome? %v\n", stringHelper.IsPalindrome("racecar"))

	// Example: Math utilities with error handling
	mathHelper := utils.NewMathHelper()
	result, err := mathHelper.Divide(10, 2)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("\n🔢 Math Utils:\n")
	fmt.Printf("└─ 10 / 2 = %.2f\n", result)

	// Example: Time utilities
	timeHelper := utils.NewTimeHelper()
	fmt.Printf("\n⏰ Time Utils:\n")
	fmt.Printf("├─ Current time: %s\n", timeHelper.FormatDateTime(time.Now()))
	fmt.Printf("└─ Is today weekend? %v\n", timeHelper.IsWeekend(time.Now()))
}

func shouldRunTradingDemo() bool {
	// Check if we have valid looking API credentials
	apiKey := os.Getenv("BINANCE_API_KEY")
	secretKey := os.Getenv("BINANCE_SECRET_KEY")

	if apiKey == "" || secretKey == "" {
		return false
	}

	// Basic validation - real API keys are usually 64 chars
	if len(apiKey) < 32 || len(secretKey) < 32 {
		return false
	}

	return true
}

func runTradingDemo() {
	fmt.Println("\n" + strings.Repeat("=", 50))
	fmt.Println("🚀 Initializing Binance Futures Trading Client...")

	ctx := context.Background()
	tradingClient, err := trading.NewTradingClient()
	if err != nil {
		log.Printf("❌ Failed to initialize trading client: %v", err)
		displayTradingInstructions()
		return
	}

	// Display account summary
	if err := tradingClient.DisplayAccountSummary(ctx); err != nil {
		log.Printf("❌ Failed to display account summary: %v", err)
		displayErrorHelp(err)
		return
	}

	// Get specific tradable balance
	tradableBalance, err := tradingClient.GetTradableBalance(ctx)
	if err != nil {
		log.Printf("❌ Failed to get tradable balance: %v", err)
	} else {
		fmt.Printf("\n✅ Ready to trade with: %.4f USDT\n", tradableBalance)
	}
}

func displayErrorHelp(err error) {
	fmt.Println("\n🆘 Common Solutions:")
	errorMsg := err.Error()

	if strings.Contains(errorMsg, "Invalid API-key") {
		fmt.Println("├─ Check if your API key is correct")
		fmt.Println("├─ Ensure API key has Futures trading permissions")
		fmt.Println("├─ Verify IP address is whitelisted (if IP restriction is enabled)")
		fmt.Println("└─ Make sure you're using the correct testnet/mainnet API key")
	} else if strings.Contains(errorMsg, "Timestamp") {
		fmt.Println("├─ Check system time synchronization")
		fmt.Println("└─ Server time might be out of sync")
	} else if strings.Contains(errorMsg, "signature") {
		fmt.Println("├─ Check if your secret key is correct")
		fmt.Println("└─ Ensure there are no extra spaces in API credentials")
	} else {
		fmt.Println("├─ Check network connection")
		fmt.Println("├─ Verify API credentials")
		fmt.Println("└─ Check Binance API status")
	}
}

func displayTradingInstructions() {
	fmt.Println("\n📋 To test Binance Futures connection:")
	fmt.Println("1. Create a Binance account and get API credentials")
	fmt.Println("2. Enable Futures trading on your account")
	fmt.Println("3. Create API key with Futures permissions")
	fmt.Println("4. Update .env file with your credentials:")
	fmt.Println("   BINANCE_API_KEY=your_api_key")
	fmt.Println("   BINANCE_SECRET_KEY=your_secret_key")
	fmt.Println("   USE_TESTNET=true  # Use testnet for safe testing")
	fmt.Println("5. Run the program again")

	fmt.Println("\n🔗 Useful links:")
	fmt.Println("├─ Binance Futures Testnet: https://testnet.binancefuture.com")
	fmt.Println("├─ API Documentation: https://binance-docs.github.io/apidocs/futures/en/")
	fmt.Println("└─ Create API Key: https://www.binance.com/en/my/settings/api-management")
}

// greetUser returns a personalized greeting
func greetUser(name string) string {
	return fmt.Sprintf("Hello, %s! Ready to code in Go?", name)
}
