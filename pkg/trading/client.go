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
			if pos.MaxNotionalValue != "" {
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

	mode := futures.MarginTypeIsolated
	if marginMode == "CROSSED" {
		mode = futures.MarginTypeCrossed
	}

	err := tc.BinanceClient.NewChangeMarginTypeService().
		Symbol(symbol).
		MarginType(mode).
		Do(ctx)

	if err != nil {
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
	quantityStr, err := tc.formatQuantity(ctx, symbol, quantity)
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
		priceStr, err := tc.formatPrice(ctx, symbol, price)
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
	quantityStr, err := tc.formatQuantity(ctx, symbol, quantity)
	if err != nil {
		return nil, fmt.Errorf("failed to format quantity: %w", err)
	}

	stopPriceStr, err := tc.formatPrice(ctx, symbol, stopPrice)
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
	quantityStr, err := tc.formatQuantity(ctx, symbol, quantity)
	if err != nil {
		return nil, fmt.Errorf("failed to format quantity: %w", err)
	}

	takeProfitPriceStr, err := tc.formatPrice(ctx, symbol, takeProfitPrice)
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

// CleanupOrphaneOrders ตรวจสอบและปิด orders ที่ไม่มี position แล้ว
func (tc *TradingClient) CleanupOrphaneOrders(ctx context.Context) error {
	fmt.Println("🧹 Cleaning up orphaned orders (orders without positions)...")

	// ดึงข้อมูล positions ที่มีอยู่
	positions, err := tc.GetPositions(ctx)
	if err != nil {
		return fmt.Errorf("failed to get positions: %w", err)
	}

	// สร้าง map ของ symbols ที่มี position
	positionSymbols := make(map[string]bool)
	for _, pos := range positions {
		positionSymbols[pos.Symbol] = true
	}

	fmt.Printf("📊 Found %d active positions\n", len(positions))
	if len(positions) > 0 {
		fmt.Println("💼 Active positions:")
		for _, pos := range positions {
			fmt.Printf("   %s: %s %.6f @ %.4f (PnL: %.4f USDT)\n",
				pos.Symbol, pos.Side, pos.PositionAmt, pos.EntryPrice, pos.UnrealizedProfit)
		}
	}

	// ดึงข้อมูล open orders
	orders, err := tc.GetOpenOrders(ctx)
	if err != nil {
		return fmt.Errorf("failed to get open orders: %w", err)
	}

	fmt.Printf("📋 Found %d open orders\n", len(orders))

	var orphanedOrders []Order
	var keepOrders []Order

	// แยก orders ที่เป็น orphaned (ไม่มี position) และที่ต้องเก็บไว้
	for _, order := range orders {
		// เช็คว่าเป็น take profit หรือ stop loss order
		isTakeProfitOrStopLoss := order.ReduceOnly ||
			order.Type == "TAKE_PROFIT_MARKET" ||
			order.Type == "STOP_MARKET" ||
			order.Type == "TRAILING_STOP_MARKET"

		if isTakeProfitOrStopLoss && !positionSymbols[order.Symbol] {
			// Order นี้เป็น TP/SL แต่ไม่มี position แล้ว = orphaned
			orphanedOrders = append(orphanedOrders, order)
		} else {
			keepOrders = append(keepOrders, order)
		}
	}

	if len(orphanedOrders) == 0 {
		fmt.Println("✅ No orphaned orders found - all orders have corresponding positions")
		return nil
	}

	fmt.Printf("🗑️  Found %d orphaned orders to cancel:\n", len(orphanedOrders))

	canceledCount := 0
	for _, order := range orphanedOrders {
		fmt.Printf("   Canceling %s %s %s Order #%d (Price: %.6f)\n",
			order.Symbol, order.Type, order.Side, order.OrderID,
			func() float64 {
				if order.StopPrice > 0 {
					return order.StopPrice
				}
				return order.Price
			}())

		err := tc.CancelOrder(ctx, order.Symbol, order.OrderID)
		if err != nil {
			fmt.Printf("   ❌ Failed to cancel order %d: %v\n", order.OrderID, err)
		} else {
			fmt.Printf("   ✅ Successfully canceled order %d\n", order.OrderID)
			canceledCount++
		}
	}

	fmt.Printf("🧹 Cleanup completed: %d/%d orders canceled\n", canceledCount, len(orphanedOrders))
	fmt.Printf("📋 Remaining orders: %d\n", len(keepOrders))

	if len(keepOrders) > 0 {
		fmt.Println("📝 Remaining active orders:")
		for _, order := range keepOrders {
			fmt.Printf("   %s %s %s: %.6f @ %.6f\n",
				order.Symbol, order.Type, order.Side, order.OrigQty,
				func() float64 {
					if order.StopPrice > 0 {
						return order.StopPrice
					}
					return order.Price
				}())
		}
	}

	return nil
}

// formatQuantity formats quantity according to symbol's step size
func (tc *TradingClient) formatQuantity(ctx context.Context, symbol string, quantity float64) (string, error) {
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

// formatPrice formats price according to symbol's tick size
func (tc *TradingClient) formatPrice(ctx context.Context, symbol string, price float64) (string, error) {
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
