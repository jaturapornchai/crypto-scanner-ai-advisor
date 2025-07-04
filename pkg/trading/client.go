package trading

import (
	"context"
	"fmt"
	"log"
	"math"
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

// Client is an alias for TradingClient for backward compatibility
type Client = TradingClient

// NewClient creates a new trading client (alias for NewTradingClient)
func NewClient(config interface{}) (*Client, error) {
	return NewTradingClient()
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

	// For swing trading, use total wallet balance instead of available balance
	// This allows us to use funds that are locked in orders for new positions
	return usdtBalance.WalletBalance, nil
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

// OrderRequest represents a trading order request
type OrderRequest struct {
	Symbol        string
	Side          string // BUY or SELL
	Type          string // MARKET, LIMIT, STOP_MARKET, TAKE_PROFIT_MARKET
	Quantity      string
	Price         string
	StopPrice     string
	ReduceOnly    bool
	ClosePosition bool
}

// OrderResponse represents a trading order response
type OrderResponse struct {
	OrderID     string
	Symbol      string
	Status      string
	ExecutedQty float64
	AvgPrice    float64
}

// Position represents a trading position
type Position struct {
	Symbol           string  `json:"symbol"`
	PositionAmt      float64 `json:"positionAmt"`
	EntryPrice       float64 `json:"entryPrice"`
	MarkPrice        float64 `json:"markPrice"`
	UnrealizedProfit float64 `json:"unrealizedProfit"`
	Leverage         int     `json:"leverage"`
	Side             string  `json:"side"`
}

// Order represents an order
type Order struct {
	OrderID       int64   `json:"orderId"`
	Symbol        string  `json:"symbol"`
	Status        string  `json:"status"`
	Side          string  `json:"side"`
	Type          string  `json:"type"`
	OrigQty       float64 `json:"origQty"`
	Price         float64 `json:"price"`
	StopPrice     float64 `json:"stopPrice"`
	ReduceOnly    bool    `json:"reduceOnly"`
	ClosePosition bool    `json:"closePosition"`
}

// GetLeverage gets current leverage for a symbol
func (tc *TradingClient) GetLeverage(symbol string) (int, error) {
	ctx := context.Background()

	// Get position information
	positions, err := tc.BinanceClient.NewGetPositionRiskService().Do(ctx)
	if err != nil {
		return 0, fmt.Errorf("failed to get position info: %w", err)
	}

	for _, pos := range positions {
		if pos.Symbol == symbol {
			leverage, err := strconv.Atoi(pos.Leverage)
			if err != nil {
				return 0, fmt.Errorf("failed to parse leverage: %w", err)
			}
			return leverage, nil
		}
	}

	return 0, fmt.Errorf("symbol %s not found", symbol)
}

// ChangeLeverage changes leverage for a symbol
func (tc *TradingClient) ChangeLeverage(symbol string, leverage int) error {
	ctx := context.Background()

	_, err := tc.BinanceClient.NewChangeLeverageService().
		Symbol(symbol).
		Leverage(leverage).
		Do(ctx)

	if err != nil {
		return fmt.Errorf("failed to change leverage: %w", err)
	}

	return nil
}

// GetMarginMode gets current margin mode for a symbol
func (tc *TradingClient) GetMarginMode(symbol string) (string, error) {
	ctx := context.Background()

	// Get position information
	positions, err := tc.BinanceClient.NewGetPositionRiskService().Do(ctx)
	if err != nil {
		return "", fmt.Errorf("failed to get position info: %w", err)
	}

	for _, pos := range positions {
		if pos.Symbol == symbol {
			// Use MarginType field directly (most reliable)
			if pos.MarginType == "isolated" {
				return "ISOLATED", nil
			} else if pos.MarginType == "cross" {
				return "CROSSED", nil
			}

			// Fallback: if MarginType is empty or unknown, use MaxNotionalValue method
			if pos.MaxNotionalValue != "" && pos.MaxNotionalValue != "0" {
				return "CROSSED", nil
			}
			return "ISOLATED", nil
		}
	}

	return "", fmt.Errorf("symbol %s not found", symbol)
}

// ChangeMarginMode changes margin mode for a symbol
func (tc *TradingClient) ChangeMarginMode(symbol string, marginMode string) error {
	ctx := context.Background()

	var mode futures.MarginType
	if marginMode == "ISOLATED" {
		mode = futures.MarginTypeIsolated
	} else if marginMode == "CROSSED" {
		mode = futures.MarginTypeCrossed
	} else {
		return fmt.Errorf("invalid margin mode: %s (must be ISOLATED or CROSSED)", marginMode)
	}

	err := tc.BinanceClient.NewChangeMarginTypeService().
		Symbol(symbol).
		MarginType(mode).
		Do(ctx)

	if err != nil {
		// Check for specific Binance error messages
		if strings.Contains(err.Error(), "No need to change margin type") {
			// Already in the requested margin mode, so this is not an error
			return nil
		}
		return fmt.Errorf("failed to change margin mode: %w", err)
	}

	return nil
}

// CreateOrder creates a new trading order
func (tc *TradingClient) CreateOrder(order *OrderRequest) (*OrderResponse, error) {
	ctx := context.Background()

	service := tc.BinanceClient.NewCreateOrderService().
		Symbol(order.Symbol).
		Side(futures.SideType(order.Side)).
		Type(futures.OrderType(order.Type))

	// Set quantity if provided
	if order.Quantity != "" {
		service = service.Quantity(order.Quantity)
	}

	// Set price for limit orders
	if order.Price != "" {
		service = service.Price(order.Price)
	}

	// Set stop price for stop orders
	if order.StopPrice != "" {
		service = service.StopPrice(order.StopPrice)
	}

	// Set reduce only flag
	if order.ReduceOnly {
		service = service.ReduceOnly(true)
	}

	// Set close position flag
	if order.ClosePosition {
		service = service.ClosePosition(true)
	}

	result, err := service.Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to create order: %w", err)
	}

	return &OrderResponse{
		OrderID: fmt.Sprintf("%d", result.OrderID),
		Symbol:  result.Symbol,
		Status:  string(result.Status),
	}, nil
}

// AccountInfo represents account information
type AccountInfo struct {
	Assets []AccountAsset
}

// AccountAsset represents an account asset
type AccountAsset struct {
	Asset         string
	WalletBalance string
	MarginBalance string
}

// GetAccountInfoSimple gets account information including balances (simplified version)
func (tc *TradingClient) GetAccountInfoSimple() (*AccountInfo, error) {
	ctx := context.Background()

	account, err := tc.BinanceClient.NewGetAccountService().Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get account info: %w", err)
	}

	var assets []AccountAsset
	for _, asset := range account.Assets {
		assets = append(assets, AccountAsset{
			Asset:         asset.Asset,
			WalletBalance: asset.WalletBalance,
			MarginBalance: asset.MarginBalance,
		})
	}

	return &AccountInfo{
		Assets: assets,
	}, nil
}

// GetTicker gets current price ticker for a symbol
func (tc *TradingClient) GetTicker(symbol string) (*TickerPrice, error) {
	ctx := context.Background()

	ticker, err := tc.BinanceClient.NewListPriceChangeStatsService().
		Symbol(symbol).
		Do(ctx)

	if err != nil {
		return nil, fmt.Errorf("failed to get ticker: %w", err)
	}

	if len(ticker) == 0 {
		return nil, fmt.Errorf("no ticker data for symbol %s", symbol)
	}

	return &TickerPrice{
		Symbol: ticker[0].Symbol,
		Price:  ticker[0].LastPrice,
	}, nil
}

// TickerPrice represents ticker price information
type TickerPrice struct {
	Symbol string
	Price  string
}

// GetUSDTSymbols gets all USDT trading symbols
func (tc *TradingClient) GetUSDTSymbols() ([]string, error) {
	ctx := context.Background()

	exchangeInfo, err := tc.BinanceClient.NewExchangeInfoService().Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get exchange info: %w", err)
	}

	var symbols []string
	for _, symbol := range exchangeInfo.Symbols {
		if symbol.QuoteAsset == "USDT" && symbol.Status == "TRADING" {
			symbols = append(symbols, symbol.Symbol)
		}
	}

	return symbols, nil
}

// GetKlines gets kline/candlestick data for a symbol
func (tc *TradingClient) GetKlines(symbol string, interval string, limit int) ([][]interface{}, error) {
	ctx := context.Background()

	klines, err := tc.BinanceClient.NewKlinesService().
		Symbol(symbol).
		Interval(interval).
		Limit(limit).
		Do(ctx)

	if err != nil {
		return nil, fmt.Errorf("failed to get klines: %w", err)
	}

	// Convert to interface{} slice for compatibility
	var result [][]interface{}
	for _, kline := range klines {
		row := []interface{}{
			kline.OpenTime,
			kline.Open,
			kline.High,
			kline.Low,
			kline.Close,
			kline.Volume,
			kline.CloseTime,
		}
		result = append(result, row)
	}

	return result, nil
}

// PlaceOrder places a market order
func (tc *TradingClient) PlaceOrder(ctx context.Context, symbol, side, orderType string, quantity, price float64) (*OrderResponse, error) {
	// Get symbol info to determine proper precision
	quantityStr, err := tc.FormatQuantity(ctx, symbol, quantity)
	if err != nil {
		return nil, fmt.Errorf("failed to format quantity: %w", err)
	}

	service := tc.BinanceClient.NewCreateOrderService().
		Symbol(symbol).
		Side(futures.SideType(side)).
		Type(futures.OrderType(orderType)).
		Quantity(quantityStr)

	// Add price for limit orders
	if orderType == "LIMIT" && price > 0 {
		priceStr, err := tc.FormatPrice(ctx, symbol, price)
		if err != nil {
			return nil, fmt.Errorf("failed to format price: %w", err)
		}
		service = service.Price(priceStr)
	}

	result, err := service.Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to place order: %w", err)
	}

	return &OrderResponse{
		OrderID:     fmt.Sprintf("%d", result.OrderID),
		Status:      string(result.Status),
		ExecutedQty: parseFloat(result.ExecutedQuantity),
		AvgPrice:    parseFloat(result.AvgPrice),
	}, nil
}

// PlaceStopOrder places a stop loss order
func (tc *TradingClient) PlaceStopOrder(ctx context.Context, symbol, side string, quantity, stopPrice float64) (*OrderResponse, error) {
	quantityStr, err := tc.FormatQuantity(ctx, symbol, quantity)
	if err != nil {
		return nil, fmt.Errorf("failed to format quantity: %w", err)
	}

	stopPriceStr, err := tc.FormatPrice(ctx, symbol, stopPrice)
	if err != nil {
		return nil, fmt.Errorf("failed to format stop price: %w", err)
	}

	service := tc.BinanceClient.NewCreateOrderService().
		Symbol(symbol).
		Side(futures.SideType(side)).
		Type(futures.OrderTypeStopMarket).
		Quantity(quantityStr).
		StopPrice(stopPriceStr).
		ReduceOnly(true)

	result, err := service.Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to place stop order: %w", err)
	}

	return &OrderResponse{
		OrderID:     fmt.Sprintf("%d", result.OrderID),
		Status:      string(result.Status),
		ExecutedQty: parseFloat(result.ExecutedQuantity),
		AvgPrice:    parseFloat(result.AvgPrice),
	}, nil
}

// PlaceTakeProfitOrder places a take profit order
func (tc *TradingClient) PlaceTakeProfitOrder(ctx context.Context, symbol, side string, quantity, takeProfitPrice float64) (*OrderResponse, error) {
	quantityStr, err := tc.FormatQuantity(ctx, symbol, quantity)
	if err != nil {
		return nil, fmt.Errorf("failed to format quantity: %w", err)
	}

	takeProfitPriceStr, err := tc.FormatPrice(ctx, symbol, takeProfitPrice)
	if err != nil {
		return nil, fmt.Errorf("failed to format take profit price: %w", err)
	}

	service := tc.BinanceClient.NewCreateOrderService().
		Symbol(symbol).
		Side(futures.SideType(side)).
		Type(futures.OrderTypeTakeProfitMarket).
		Quantity(quantityStr).
		StopPrice(takeProfitPriceStr).
		ReduceOnly(true)

	result, err := service.Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to place take profit order: %w", err)
	}

	return &OrderResponse{
		OrderID:     fmt.Sprintf("%d", result.OrderID),
		Status:      string(result.Status),
		ExecutedQty: parseFloat(result.ExecutedQuantity),
		AvgPrice:    parseFloat(result.AvgPrice),
	}, nil
}

// SetLeverage sets leverage for a symbol
func (tc *TradingClient) SetLeverage(symbol string, leverage int) error {
	ctx := context.Background()

	_, err := tc.BinanceClient.NewChangeLeverageService().
		Symbol(symbol).
		Leverage(leverage).
		Do(ctx)

	if err != nil {
		return fmt.Errorf("failed to set leverage: %w", err)
	}

	return nil
}

// GetPositions retrieves all current positions
func (tc *TradingClient) GetPositions(ctx context.Context) ([]Position, error) {
	positions, err := tc.BinanceClient.NewGetPositionRiskService().Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get positions: %w", err)
	}

	var result []Position
	for _, pos := range positions {
		positionAmt, _ := strconv.ParseFloat(pos.PositionAmt, 64)
		// Only include positions with non-zero amount
		if positionAmt != 0 {
			entryPrice, _ := strconv.ParseFloat(pos.EntryPrice, 64)
			markPrice, _ := strconv.ParseFloat(pos.MarkPrice, 64)
			unrealizedProfit, _ := strconv.ParseFloat(pos.UnRealizedProfit, 64)
			leverage, _ := strconv.Atoi(pos.Leverage)

			side := "LONG"
			if positionAmt < 0 {
				side = "SHORT"
				positionAmt = -positionAmt // Make position amount positive for display
			}

			result = append(result, Position{
				Symbol:           pos.Symbol,
				PositionAmt:      positionAmt,
				EntryPrice:       entryPrice,
				MarkPrice:        markPrice,
				UnrealizedProfit: unrealizedProfit,
				Leverage:         leverage,
				Side:             side,
			})
		}
	}

	return result, nil
}

// GetOpenOrders retrieves all open orders
func (tc *TradingClient) GetOpenOrders(ctx context.Context) ([]Order, error) {
	orders, err := tc.BinanceClient.NewListOpenOrdersService().Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get open orders: %w", err)
	}

	var result []Order
	for _, order := range orders {
		origQty, _ := strconv.ParseFloat(order.OrigQuantity, 64)
		price, _ := strconv.ParseFloat(order.Price, 64)
		stopPrice, _ := strconv.ParseFloat(order.StopPrice, 64)

		result = append(result, Order{
			OrderID:       order.OrderID,
			Symbol:        order.Symbol,
			Status:        string(order.Status),
			Side:          string(order.Side),
			Type:          string(order.Type),
			OrigQty:       origQty,
			Price:         price,
			StopPrice:     stopPrice,
			ReduceOnly:    order.ReduceOnly,
			ClosePosition: order.ClosePosition,
		})
	}

	return result, nil
}

// CancelOrder cancels an order by order ID
func (tc *TradingClient) CancelOrder(ctx context.Context, symbol string, orderID int64) error {
	_, err := tc.BinanceClient.NewCancelOrderService().
		Symbol(symbol).
		OrderID(orderID).
		Do(ctx)

	if err != nil {
		return fmt.Errorf("failed to cancel order %d for %s: %w", orderID, symbol, err)
	}

	return nil
}

// CleanupOrphaneOrders Simple cleanup: 1 position = 2 orders (ไม่สนใจประเภท), ไม่มี position = ปิดทุก orders
func (tc *TradingClient) CleanupOrphaneOrders(ctx context.Context) error {
	fmt.Println("🧹 Comprehensive Order/Position Cleanup")
	fmt.Println("   Rules: 1 position = exactly 2 orders, no position = no orders")
	fmt.Println("   If position has < 2 orders → close position + cancel all orders")

	// Get positions
	positions, err := tc.GetPositions(ctx)
	if err != nil {
		return fmt.Errorf("failed to get positions: %w", err)
	}

	// Create position map with actual quantities
	positionMap := make(map[string]float64)
	for _, pos := range positions {
		if pos.PositionAmt != 0 {
			positionMap[pos.Symbol] = pos.PositionAmt
		}
	}

	// Get open orders
	orders, err := tc.GetOpenOrders(ctx)
	if err != nil {
		return fmt.Errorf("failed to get open orders: %w", err)
	}

	fmt.Printf("📊 Analysis: %d positions, %d orders\n", len(positionMap), len(orders))

	// Group orders by symbol
	ordersBySymbol := make(map[string][]Order)
	for _, order := range orders {
		ordersBySymbol[order.Symbol] = append(ordersBySymbol[order.Symbol], order)
	}

	// Get all symbols (from both positions and orders)
	allSymbols := make(map[string]bool)
	for symbol := range positionMap {
		allSymbols[symbol] = true
	}
	for symbol := range ordersBySymbol {
		allSymbols[symbol] = true
	}

	// Analysis and action planning
	var symbolsToClosePositions []string
	var ordersToCancel []Order
	var symbolsWithCorrectSetup []string
	var problematicSymbols []string

	fmt.Println("\n🔍 Detailed Analysis by Symbol:")
	
	for symbol := range allSymbols {
		positionAmt := positionMap[symbol]
		symbolOrders := ordersBySymbol[symbol]
		hasPosition := positionAmt != 0
		orderCount := len(symbolOrders)

		fmt.Printf("   %s: Position=%.4f, Orders=%d", symbol, positionAmt, orderCount)

		if !hasPosition {
			// No position - should have no orders
			if orderCount > 0 {
				fmt.Printf(" → Cancel %d orphaned orders\n", orderCount)
				ordersToCancel = append(ordersToCancel, symbolOrders...)
				problematicSymbols = append(problematicSymbols, symbol)
			} else {
				fmt.Printf(" → ✅ Correct (no position, no orders)\n")
			}
		} else {
			// Has position - should have exactly 2 orders
			if orderCount < 2 {
				fmt.Printf(" → ❌ Close position (insufficient orders)\n")
				symbolsToClosePositions = append(symbolsToClosePositions, symbol)
				ordersToCancel = append(ordersToCancel, symbolOrders...)
				problematicSymbols = append(problematicSymbols, symbol)
			} else if orderCount == 2 {
				fmt.Printf(" → ✅ Correct (position with 2 orders)\n")
				symbolsWithCorrectSetup = append(symbolsWithCorrectSetup, symbol)
			} else {
				fmt.Printf(" → Cancel %d excess orders (keep 2)\n", orderCount-2)
				ordersToCancel = append(ordersToCancel, symbolOrders[2:]...)
				problematicSymbols = append(problematicSymbols, symbol)
			}
		}
	}

	// Summary
	fmt.Printf("\n📋 Cleanup Summary:\n")
	fmt.Printf("   ✅ Correct symbols: %d\n", len(symbolsWithCorrectSetup))
	fmt.Printf("   ⚠️  Problematic symbols: %d\n", len(problematicSymbols))
	fmt.Printf("   🗑️  Orders to cancel: %d\n", len(ordersToCancel))
	fmt.Printf("   ❌ Positions to close: %d\n", len(symbolsToClosePositions))

	if len(problematicSymbols) == 0 {
		fmt.Println("🎉 All positions and orders are perfectly balanced!")
		return nil
	}

	// Execute cleanup actions
	fmt.Println("\n🔧 Executing Cleanup Actions:")
	
	// Step 1: Close positions that have insufficient orders
	var failedPositionCloses []string
	for _, symbol := range symbolsToClosePositions {
		fmt.Printf("   🔴 Closing position %s (insufficient orders)\n", symbol)
		if err := tc.ClosePosition(ctx, symbol); err != nil {
			fmt.Printf("      ❌ Failed to close position %s: %v\n", symbol, err)
			failedPositionCloses = append(failedPositionCloses, symbol)
		} else {
			fmt.Printf("      ✅ Position %s closed successfully\n", symbol)
		}
	}

	// Step 2: Cancel orders
	canceledCount := 0
	failedCancels := 0
	
	for _, order := range ordersToCancel {
		fmt.Printf("   🗑️  Canceling %s Order #%d\n", order.Symbol, order.OrderID)
		if err := tc.CancelOrder(ctx, order.Symbol, order.OrderID); err != nil {
			fmt.Printf("      ❌ Failed: %v\n", err)
			failedCancels++
		} else {
			canceledCount++
		}
	}

	fmt.Printf("\n✅ Cleanup Complete:\n")
	fmt.Printf("   📊 Orders canceled: %d/%d\n", canceledCount, len(ordersToCancel))
	fmt.Printf("   🔴 Positions closed: %d/%d\n", len(symbolsToClosePositions)-len(failedPositionCloses), len(symbolsToClosePositions))
	
	if failedCancels > 0 {
		fmt.Printf("   ⚠️  Failed order cancellations: %d\n", failedCancels)
	}
	
	if len(failedPositionCloses) > 0 {
		fmt.Printf("   ⚠️  Failed position closes: %d (%v)\n", len(failedPositionCloses), failedPositionCloses)
	}

	// Final verification
	fmt.Println("\n🔍 Post-Cleanup Verification:")
	if err := tc.verifyOrderPositionBalance(ctx); err != nil {
		fmt.Printf("   ⚠️  Verification found issues: %v\n", err)
	} else {
		fmt.Println("   ✅ All positions and orders are now balanced")
	}

	return nil
}

// verifyOrderPositionBalance verifies that every position has exactly 2 orders and no orphaned orders exist
func (tc *TradingClient) verifyOrderPositionBalance(ctx context.Context) error {
	// Get positions
	positions, err := tc.GetPositions(ctx)
	if err != nil {
		return fmt.Errorf("failed to get positions: %w", err)
	}

	// Create position map with actual quantities
	positionMap := make(map[string]float64)
	for _, pos := range positions {
		if pos.PositionAmt != 0 {
			positionMap[pos.Symbol] = pos.PositionAmt
		}
	}

	// Get open orders
	orders, err := tc.GetOpenOrders(ctx)
	if err != nil {
		return fmt.Errorf("failed to get open orders: %w", err)
	}

	// Group orders by symbol
	ordersBySymbol := make(map[string][]Order)
	for _, order := range orders {
		ordersBySymbol[order.Symbol] = append(ordersBySymbol[order.Symbol], order)
	}

	// Check all symbols
	allSymbols := make(map[string]bool)
	for symbol := range positionMap {
		allSymbols[symbol] = true
	}
	for symbol := range ordersBySymbol {
		allSymbols[symbol] = true
	}

	var errors []string

	for symbol := range allSymbols {
		positionAmt := positionMap[symbol]
		symbolOrders := ordersBySymbol[symbol]
		hasPosition := positionAmt != 0
		orderCount := len(symbolOrders)

		if !hasPosition && orderCount > 0 {
			errors = append(errors, fmt.Sprintf("%s: has %d orphaned orders", symbol, orderCount))
		} else if hasPosition && orderCount != 2 {
			errors = append(errors, fmt.Sprintf("%s: position exists but has %d orders (expected 2)", symbol, orderCount))
		}
	}

	if len(errors) > 0 {
		return fmt.Errorf("balance issues found: %s", strings.Join(errors, "; "))
	}

	return nil
}

// GetSwingTradingBalance returns available balance for swing trading
// This calculates usable balance by excluding only position margin, not pending orders
func (tc *TradingClient) GetSwingTradingBalance(ctx context.Context) (float64, error) {
	usdtBalance, err := tc.GetUSDTBalance(ctx)
	if err != nil {
		return 0, err
	}

	// For swing trading, we can use: Wallet Balance - Position Margin
	// We don't exclude pending orders margin since we might want to cancel/replace them
	usableBalance := usdtBalance.WalletBalance - usdtBalance.PositionInitialMargin

	// Ensure we don't return negative balance
	if usableBalance < 0 {
		usableBalance = 0
	}

	return usableBalance, nil
}

// FormatQuantity formats quantity according to symbol's step size
func (tc *TradingClient) FormatQuantity(ctx context.Context, symbol string, quantity float64) (string, error) {
	pairs, err := tc.GetUSDTPairs(ctx)
	if err != nil {
		return "", fmt.Errorf("failed to get symbol info: %w", err)
	}

	for _, pair := range pairs {
		if pair.Symbol == symbol {
			// Use quantity precision to format
			precision := pair.QuantityPrecision
			if precision < 0 {
				precision = 3 // default precision
			}

			// Ensure quantity respects step size and min quantity
			if pair.StepSize > 0 {
				quantity = math.Floor(quantity/pair.StepSize) * pair.StepSize
			}

			if quantity < pair.MinQty {
				return "", fmt.Errorf("quantity %.8f is below minimum %.8f for %s", quantity, pair.MinQty, symbol)
			}

			format := fmt.Sprintf("%%.%df", precision)
			return fmt.Sprintf(format, quantity), nil
		}
	}

	// Fallback: use 3 decimal places
	return fmt.Sprintf("%.3f", quantity), nil
}

// FormatPrice formats price according to symbol's tick size
func (tc *TradingClient) FormatPrice(ctx context.Context, symbol string, price float64) (string, error) {
	pairs, err := tc.GetUSDTPairs(ctx)
	if err != nil {
		return "", fmt.Errorf("failed to get symbol info: %w", err)
	}

	for _, pair := range pairs {
		if pair.Symbol == symbol {
			// Use price precision to format
			precision := pair.PricePrecision
			if precision < 0 {
				precision = 4 // default precision
			}

			// Ensure price respects tick size
			if pair.TickSize > 0 {
				price = math.Round(price/pair.TickSize) * pair.TickSize
			}

			format := fmt.Sprintf("%%.%df", precision)
			return fmt.Sprintf(format, price), nil
		}
	}

	// Fallback: use 4 decimal places
	return fmt.Sprintf("%.4f", price), nil
}

// parseFloat safely converts string to float64
func parseFloat(s string) float64 {
	if s == "" {
		return 0
	}
	f, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return 0
	}
	return f
}

// ClosePosition closes a position by placing a market order in the opposite direction
// Uses multiple fallback methods for stuck positions
func (tc *TradingClient) ClosePosition(ctx context.Context, symbol string) error {
	// Get current position
	positions, err := tc.GetPositions(ctx)
	if err != nil {
		return fmt.Errorf("failed to get positions: %w", err)
	}
	
	var targetPosition *Position
	for _, pos := range positions {
		if pos.Symbol == symbol && pos.PositionAmt != 0 {
			targetPosition = &pos
			break
		}
	}
	
	if targetPosition == nil {
		return fmt.Errorf("no position found for symbol %s", symbol)
	}
	
	log.Printf("Attempting to close position for %s: Size %.8f", symbol, targetPosition.PositionAmt)
	
	// Try multiple methods in sequence
	methods := []func() error{
		func() error { return tc.closeWithReduceOnly(ctx, symbol, targetPosition) },
		func() error { return tc.closeWithClosePositionFlag(ctx, symbol, targetPosition) },
		func() error { return tc.closeWithMarketOrder(ctx, symbol, targetPosition) },
		func() error { return tc.closeWithPrecisionRounding(ctx, symbol, targetPosition) },
		func() error { return tc.closeWithMultipleOrders(ctx, symbol, targetPosition) },
		func() error { return tc.forceCloseWithHedge(ctx, symbol, targetPosition) },
	}
	
	var lastErr error
	for i, method := range methods {
		log.Printf("Trying close method %d for %s", i+1, symbol)
		err := method()
		if err == nil {
			log.Printf("Successfully closed position for %s using method %d", symbol, i+1)
			return nil
		}
		lastErr = err
		log.Printf("Method %d failed for %s: %v", i+1, symbol, err)
	}
	
	return fmt.Errorf("all close methods failed for %s, last error: %w", symbol, lastErr)
}

// Method 1: Standard ReduceOnly approach
func (tc *TradingClient) closeWithReduceOnly(ctx context.Context, symbol string, position *Position) error {
	side := futures.SideTypeSell
	if position.PositionAmt < 0 {
		side = futures.SideTypeBuy
	}
	
	quantity := fmt.Sprintf("%.8f", math.Abs(position.PositionAmt))
	
	_, err := tc.BinanceClient.NewCreateOrderService().
		Symbol(symbol).
		Side(side).
		Type(futures.OrderTypeMarket).
		Quantity(quantity).
		ReduceOnly(true).
		Do(ctx)
	
	return err
}

// Method 2: ClosePosition flag approach
func (tc *TradingClient) closeWithClosePositionFlag(ctx context.Context, symbol string, position *Position) error {
	side := futures.SideTypeSell
	if position.PositionAmt < 0 {
		side = futures.SideTypeBuy
	}
	
	quantity := fmt.Sprintf("%.8f", math.Abs(position.PositionAmt))
	
	_, err := tc.BinanceClient.NewCreateOrderService().
		Symbol(symbol).
		Side(side).
		Type(futures.OrderTypeMarket).
		Quantity(quantity).
		ClosePosition(true).
		Do(ctx)
	
	return err
}

// Method 3: Plain market order (no flags)
func (tc *TradingClient) closeWithMarketOrder(ctx context.Context, symbol string, position *Position) error {
	side := futures.SideTypeSell
	if position.PositionAmt < 0 {
		side = futures.SideTypeBuy
	}
	
	quantity := fmt.Sprintf("%.8f", math.Abs(position.PositionAmt))
	
	_, err := tc.BinanceClient.NewCreateOrderService().
		Symbol(symbol).
		Side(side).
		Type(futures.OrderTypeMarket).
		Quantity(quantity).
		Do(ctx)
	
	return err
}

// Method 4: Round quantity to avoid precision errors
func (tc *TradingClient) closeWithPrecisionRounding(ctx context.Context, symbol string, position *Position) error {
	side := futures.SideTypeSell
	if position.PositionAmt < 0 {
		side = futures.SideTypeBuy
	}
	
	// Get symbol info for precision
	exchangeInfo, err := tc.BinanceClient.NewExchangeInfoService().Do(ctx)
	if err != nil {
		return fmt.Errorf("failed to get exchange info: %w", err)
	}
	
	var stepSize float64 = 0.001 // default
	for _, symbolInfo := range exchangeInfo.Symbols {
		if symbolInfo.Symbol == symbol {
			for _, filter := range symbolInfo.Filters {
				if filter["filterType"] == "LOT_SIZE" {
					if ss, ok := filter["stepSize"].(string); ok {
						if parsed, err := strconv.ParseFloat(ss, 64); err == nil {
							stepSize = parsed
						}
					}
				}
			}
			break
		}
	}
	
	// Round quantity to step size
	absAmount := math.Abs(position.PositionAmt)
	roundedAmount := math.Floor(absAmount/stepSize) * stepSize
	
	if roundedAmount <= 0 {
		return fmt.Errorf("rounded quantity is zero")
	}
	
	quantity := fmt.Sprintf("%.8f", roundedAmount)
	
	_, err = tc.BinanceClient.NewCreateOrderService().
		Symbol(symbol).
		Side(side).
		Type(futures.OrderTypeMarket).
		Quantity(quantity).
		ReduceOnly(true).
		Do(ctx)
	
	return err
}

// Method 5: Close in multiple smaller orders
func (tc *TradingClient) closeWithMultipleOrders(ctx context.Context, symbol string, position *Position) error {
	side := futures.SideTypeSell
	if position.PositionAmt < 0 {
		side = futures.SideTypeBuy
	}
	
	absAmount := math.Abs(position.PositionAmt)
	numOrders := 3
	orderSize := absAmount / float64(numOrders)
	
	for i := 0; i < numOrders; i++ {
		quantity := fmt.Sprintf("%.8f", orderSize)
		
		_, err := tc.BinanceClient.NewCreateOrderService().
			Symbol(symbol).
			Side(side).
			Type(futures.OrderTypeMarket).
			Quantity(quantity).
			ReduceOnly(true).
			Do(ctx)
		
		if err != nil {
			return fmt.Errorf("failed on order %d: %w", i+1, err)
		}
		
		// Small delay between orders
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			// Continue immediately
		}
	}
	
	return nil
}

// Method 6: Force close by opening opposite position then closing both
func (tc *TradingClient) forceCloseWithHedge(ctx context.Context, symbol string, position *Position) error {
	log.Printf("WARNING: Using hedge method for %s - this opens a temporary opposite position", symbol)
	
	// Determine opposite side for hedge
	hedgeSide := futures.SideTypeBuy
	if position.PositionAmt < 0 {
		hedgeSide = futures.SideTypeSell
	}
	
	absAmount := math.Abs(position.PositionAmt)
	quantity := fmt.Sprintf("%.8f", absAmount)
	
	// Step 1: Open opposite position (hedge)
	_, err := tc.BinanceClient.NewCreateOrderService().
		Symbol(symbol).
		Side(hedgeSide).
		Type(futures.OrderTypeMarket).
		Quantity(quantity).
		Do(ctx)
	
	if err != nil {
		return fmt.Errorf("failed to create hedge position: %w", err)
	}
	
	log.Printf("Created hedge position for %s, now attempting to close all", symbol)
	
	// Step 2: Wait a moment for position to update
	// (In production, you might want to poll for position updates)
	
	// Step 3: Try to close the now-neutral position
	// Since we have equal opposite positions, they should cancel out
	// But if not, try to close both individually
	
	// Get updated positions
	positions, err := tc.GetPositions(ctx)
	if err != nil {
		return fmt.Errorf("failed to get updated positions after hedge: %w", err)
	}
	
	for _, pos := range positions {
		if pos.Symbol == symbol && pos.PositionAmt != 0 {
			// Try to close remaining position
			side := futures.SideTypeSell
			if pos.PositionAmt < 0 {
				side = futures.SideTypeBuy
			}
			
			qty := fmt.Sprintf("%.8f", math.Abs(pos.PositionAmt))
			
			_, err := tc.BinanceClient.NewCreateOrderService().
				Symbol(symbol).
				Side(side).
				Type(futures.OrderTypeMarket).
				Quantity(qty).
				ReduceOnly(true).
				Do(ctx)
			
			if err != nil {
				log.Printf("Warning: Failed to close remaining position after hedge for %s: %v", symbol, err)
			}
		}
	}
	
	return nil
}
