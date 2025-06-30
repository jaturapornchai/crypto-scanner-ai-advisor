package trading

import (
	"context"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	"github.com/adshao/go-binance/v2/futures"
	"github.com/joho/godotenv"
)

// TradingClient represents a unified trading client
type TradingClient struct {
	BinanceClient *futures.Client
	UseTestnet    bool
}

// NewTradingClient creates a new trading client
func NewTradingClient() (*TradingClient, error) {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: Could not load .env file: %v", err)
	}

	apiKey := os.Getenv("BINANCE_API_KEY")
	secretKey := os.Getenv("BINANCE_SECRET_KEY")
	useTestnetStr := os.Getenv("USE_TESTNET")

	if apiKey == "" || secretKey == "" {
		return nil, fmt.Errorf("BINANCE_API_KEY and BINANCE_SECRET_KEY must be set")
	}

	useTestnet, _ := strconv.ParseBool(useTestnetStr)

	// Initialize Binance Futures client
	futures.UseTestnet = useTestnet
	binanceClient := futures.NewClient(apiKey, secretKey)

	return &TradingClient{
		BinanceClient: binanceClient,
		UseTestnet:    useTestnet,
	}, nil
}

// AccountBalance represents account balance information
type AccountBalance struct {
	Asset                  string  `json:"asset"`
	WalletBalance          float64 `json:"walletBalance"`
	UnrealizedProfit       float64 `json:"unrealizedProfit"`
	MarginBalance          float64 `json:"marginBalance"`
	MaintMargin            float64 `json:"maintMargin"`
	InitialMargin          float64 `json:"initialMargin"`
	PositionInitialMargin  float64 `json:"positionInitialMargin"`
	OpenOrderInitialMargin float64 `json:"openOrderInitialMargin"`
	MaxWithdrawAmount      float64 `json:"maxWithdrawAmount"`
	CrossWalletBalance     float64 `json:"crossWalletBalance"`
	CrossUnPnl             float64 `json:"crossUnPnl"`
	AvailableBalance       float64 `json:"availableBalance"`
}

// GetAccountInfo retrieves account information using Binance Futures API
func (tc *TradingClient) GetAccountInfo(ctx context.Context) (*futures.Account, error) {
	account, err := tc.BinanceClient.NewGetAccountService().Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get account info: %w", err)
	}
	return account, nil
}

// GetBalance retrieves account balance using Binance Futures API
func (tc *TradingClient) GetBalance(ctx context.Context) ([]*futures.AccountAsset, error) {
	account, err := tc.GetAccountInfo(ctx)
	if err != nil {
		return nil, err
	}
	return account.Assets, nil
}

// GetUSDTBalance retrieves USDT balance specifically
func (tc *TradingClient) GetUSDTBalance(ctx context.Context) (*AccountBalance, error) {
	balances, err := tc.GetBalance(ctx)
	if err != nil {
		return nil, err
	}

	for _, balance := range balances {
		if balance.Asset == "USDT" {
			walletBalance, _ := strconv.ParseFloat(balance.WalletBalance, 64)
			unrealizedProfit, _ := strconv.ParseFloat(balance.UnrealizedProfit, 64)
			marginBalance, _ := strconv.ParseFloat(balance.MarginBalance, 64)
			maintMargin, _ := strconv.ParseFloat(balance.MaintMargin, 64)
			initialMargin, _ := strconv.ParseFloat(balance.InitialMargin, 64)
			positionInitialMargin, _ := strconv.ParseFloat(balance.PositionInitialMargin, 64)
			openOrderInitialMargin, _ := strconv.ParseFloat(balance.OpenOrderInitialMargin, 64)
			maxWithdrawAmount, _ := strconv.ParseFloat(balance.MaxWithdrawAmount, 64)
			crossWalletBalance, _ := strconv.ParseFloat(balance.CrossWalletBalance, 64)
			crossUnPnl, _ := strconv.ParseFloat(balance.CrossUnPnl, 64)
			availableBalance, _ := strconv.ParseFloat(balance.AvailableBalance, 64)

			return &AccountBalance{
				Asset:                  balance.Asset,
				WalletBalance:          walletBalance,
				UnrealizedProfit:       unrealizedProfit,
				MarginBalance:          marginBalance,
				MaintMargin:            maintMargin,
				InitialMargin:          initialMargin,
				PositionInitialMargin:  positionInitialMargin,
				OpenOrderInitialMargin: openOrderInitialMargin,
				MaxWithdrawAmount:      maxWithdrawAmount,
				CrossWalletBalance:     crossWalletBalance,
				CrossUnPnl:             crossUnPnl,
				AvailableBalance:       availableBalance,
			}, nil
		}
	}

	return nil, fmt.Errorf("USDT balance not found")
}

// GetTradableBalance returns the amount available for trading
func (tc *TradingClient) GetTradableBalance(ctx context.Context) (float64, error) {
	usdtBalance, err := tc.GetUSDTBalance(ctx)
	if err != nil {
		return 0, err
	}

	// Available balance is what can be used for new positions
	return usdtBalance.AvailableBalance, nil
}

// DisplayAccountSummary prints detailed account information
func (tc *TradingClient) DisplayAccountSummary(ctx context.Context) error {
	fmt.Println("=== Binance Futures Account Summary ===")

	if tc.UseTestnet {
		fmt.Println("🧪 Using TESTNET environment")
	} else {
		fmt.Println("🚀 Using LIVE environment")
	}

	account, err := tc.GetAccountInfo(ctx)
	if err != nil {
		return fmt.Errorf("failed to get account info: %w", err)
	}

	fmt.Printf("\n📊 Account Information:\n")
	fmt.Printf("├─ Can Trade: %v\n", account.CanTrade)
	fmt.Printf("├─ Can Deposit: %v\n", account.CanDeposit)
	fmt.Printf("├─ Can Withdraw: %v\n", account.CanWithdraw)
	fmt.Printf("├─ Fee Tier: %d\n", account.FeeTier)

	// Convert string values to float for display
	totalWalletBalance, _ := strconv.ParseFloat(account.TotalWalletBalance, 64)
	totalMarginBalance, _ := strconv.ParseFloat(account.TotalMarginBalance, 64)
	totalUnrealizedProfit, _ := strconv.ParseFloat(account.TotalUnrealizedProfit, 64)
	availableBalance, _ := strconv.ParseFloat(account.AvailableBalance, 64)
	maxWithdrawAmount, _ := strconv.ParseFloat(account.MaxWithdrawAmount, 64)

	fmt.Printf("\n💰 Balance Summary:\n")
	fmt.Printf("├─ Total Wallet Balance: %.4f USDT\n", totalWalletBalance)
	fmt.Printf("├─ Total Margin Balance: %.4f USDT\n", totalMarginBalance)
	fmt.Printf("├─ Unrealized Profit: %.4f USDT\n", totalUnrealizedProfit)
	fmt.Printf("├─ Available Balance: %.4f USDT\n", availableBalance)
	fmt.Printf("└─ Max Withdraw Amount: %.4f USDT\n", maxWithdrawAmount)

	// Get USDT specific balance
	usdtBalance, err := tc.GetUSDTBalance(ctx)
	if err != nil {
		return fmt.Errorf("failed to get USDT balance: %w", err)
	}

	fmt.Printf("\n💵 USDT Details:\n")
	fmt.Printf("├─ Wallet Balance: %.4f USDT\n", usdtBalance.WalletBalance)
	fmt.Printf("├─ Available for Trading: %.4f USDT\n", usdtBalance.AvailableBalance)
	fmt.Printf("├─ Margin Balance: %.4f USDT\n", usdtBalance.MarginBalance)
	fmt.Printf("├─ Position Initial Margin: %.4f USDT\n", usdtBalance.PositionInitialMargin)
	fmt.Printf("└─ Open Order Initial Margin: %.4f USDT\n", usdtBalance.OpenOrderInitialMargin)

	tradableAmount, _ := tc.GetTradableBalance(ctx)
	fmt.Printf("\n🎯 Tradable Amount: %.4f USDT\n", tradableAmount)

	return nil
}

// GetExchangeInfo retrieves exchange information including all trading pairs
func (tc *TradingClient) GetExchangeInfo(ctx context.Context) (*futures.ExchangeInfo, error) {
	exchangeInfo, err := tc.BinanceClient.NewExchangeInfoService().Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get exchange info: %w", err)
	}
	return exchangeInfo, nil
}

// TradingPair represents a trading pair information
type TradingPair struct {
	Symbol             string  `json:"symbol"`
	BaseAsset          string  `json:"baseAsset"`
	QuoteAsset         string  `json:"quoteAsset"`
	Status             string  `json:"status"`
	PricePrecision     int     `json:"pricePrecision"`
	QuantityPrecision  int     `json:"quantityPrecision"`
	BaseAssetPrecision int     `json:"baseAssetPrecision"`
	QuotePrecision     int     `json:"quotePrecision"`
	MinPrice           float64 `json:"minPrice"`
	MaxPrice           float64 `json:"maxPrice"`
	TickSize           float64 `json:"tickSize"`
	MinQty             float64 `json:"minQty"`
	MaxQty             float64 `json:"maxQty"`
	StepSize           float64 `json:"stepSize"`
	MinNotional        float64 `json:"minNotional"`
}

// GetUSDTPairs retrieves all USDT trading pairs
func (tc *TradingClient) GetUSDTPairs(ctx context.Context) ([]TradingPair, error) {
	exchangeInfo, err := tc.GetExchangeInfo(ctx)
	if err != nil {
		return nil, err
	}

	var usdtPairs []TradingPair

	for _, symbol := range exchangeInfo.Symbols {
		// Filter for USDT pairs that are actively trading
		if symbol.QuoteAsset == "USDT" && symbol.Status == "TRADING" {
			pair := TradingPair{
				Symbol:             symbol.Symbol,
				BaseAsset:          symbol.BaseAsset,
				QuoteAsset:         symbol.QuoteAsset,
				Status:             symbol.Status,
				PricePrecision:     symbol.PricePrecision,
				QuantityPrecision:  symbol.QuantityPrecision,
				BaseAssetPrecision: symbol.BaseAssetPrecision,
				QuotePrecision:     symbol.QuotePrecision,
			}

			// Extract filter information for min/max values
			for _, filter := range symbol.Filters {
				switch filter["filterType"] {
				case "PRICE_FILTER":
					if minPrice, ok := filter["minPrice"].(string); ok {
						pair.MinPrice, _ = strconv.ParseFloat(minPrice, 64)
					}
					if maxPrice, ok := filter["maxPrice"].(string); ok {
						pair.MaxPrice, _ = strconv.ParseFloat(maxPrice, 64)
					}
					if tickSize, ok := filter["tickSize"].(string); ok {
						pair.TickSize, _ = strconv.ParseFloat(tickSize, 64)
					}
				case "LOT_SIZE":
					if minQty, ok := filter["minQty"].(string); ok {
						pair.MinQty, _ = strconv.ParseFloat(minQty, 64)
					}
					if maxQty, ok := filter["maxQty"].(string); ok {
						pair.MaxQty, _ = strconv.ParseFloat(maxQty, 64)
					}
					if stepSize, ok := filter["stepSize"].(string); ok {
						pair.StepSize, _ = strconv.ParseFloat(stepSize, 64)
					}
				case "MIN_NOTIONAL":
					if minNotional, ok := filter["notional"].(string); ok {
						pair.MinNotional, _ = strconv.ParseFloat(minNotional, 64)
					}
				}
			}

			usdtPairs = append(usdtPairs, pair)
		}
	}

	return usdtPairs, nil
}

// GetPopularUSDTPairs returns commonly traded USDT pairs
func (tc *TradingClient) GetPopularUSDTPairs(ctx context.Context) ([]TradingPair, error) {
	allPairs, err := tc.GetUSDTPairs(ctx)
	if err != nil {
		return nil, err
	}

	// List of popular trading pairs
	popularSymbols := map[string]bool{
		"BTCUSDT": true, "ETHUSDT": true, "BNBUSDT": true, "ADAUSDT": true,
		"SOLUSDT": true, "XRPUSDT": true, "DOGEUSDT": true, "DOTUSDT": true,
		"MATICUSDT": true, "LTCUSDT": true, "AVAXUSDT": true, "LINKUSDT": true,
		"UNIUSDT": true, "BCHUSDT": true, "XLMUSDT": true, "VETUSDT": true,
		"FILUSDT": true, "TRXUSDT": true, "ETCUSDT": true, "THETAUSDT": true,
	}

	var popularPairs []TradingPair
	for _, pair := range allPairs {
		if popularSymbols[pair.Symbol] {
			popularPairs = append(popularPairs, pair)
		}
	}

	return popularPairs, nil
}

// DisplayUSDTPairs shows all USDT trading pairs in a formatted way
func (tc *TradingClient) DisplayUSDTPairs(ctx context.Context, showAll bool) error {
	var pairs []TradingPair
	var err error

	if showAll {
		fmt.Println("🪙 All USDT Trading Pairs on Binance Futures")
		fmt.Println(strings.Repeat("=", 60))
		pairs, err = tc.GetUSDTPairs(ctx)
	} else {
		fmt.Println("🌟 Popular USDT Trading Pairs on Binance Futures")
		fmt.Println(strings.Repeat("=", 60))
		pairs, err = tc.GetPopularUSDTPairs(ctx)
	}

	if err != nil {
		return fmt.Errorf("failed to get USDT pairs: %w", err)
	}

	fmt.Printf("Found %d active USDT trading pairs:\n\n", len(pairs))

	// Group pairs by first letter for better organization
	pairGroups := make(map[string][]TradingPair)
	for _, pair := range pairs {
		firstLetter := string(pair.BaseAsset[0])
		pairGroups[firstLetter] = append(pairGroups[firstLetter], pair)
	}

	// Sort keys
	var keys []string
	for k := range pairGroups {
		keys = append(keys, k)
	}

	// Simple sort
	for i := 0; i < len(keys); i++ {
		for j := i + 1; j < len(keys); j++ {
			if keys[i] > keys[j] {
				keys[i], keys[j] = keys[j], keys[i]
			}
		}
	}

	for _, letter := range keys {
		fmt.Printf("📂 %s:\n", letter)
		for _, pair := range pairGroups[letter] {
			fmt.Printf("   %-15s (%s/%s) - Min: $%.8f, Min Qty: %.8f\n",
				pair.Symbol, pair.BaseAsset, pair.QuoteAsset,
				pair.MinPrice, pair.MinQty)
		}
		fmt.Println()
	}

	return nil
}
