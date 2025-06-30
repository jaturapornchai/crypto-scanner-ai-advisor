package binance

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"time"
)

const (
	// Binance Futures API endpoints
	BaseURL        = "https://fapi.binance.com"
	TestnetBaseURL = "https://testnet.binancefuture.com"
	
	// API endpoints
	AccountInfoEndpoint = "/fapi/v2/account"
	BalanceEndpoint     = "/fapi/v2/balance"
)

// Client represents Binance Futures API client
type Client struct {
	APIKey     string
	SecretKey  string
	BaseURL    string
	HTTPClient *http.Client
}

// NewClient creates a new Binance client
func NewClient(apiKey, secretKey string, useTestnet bool) *Client {
	baseURL := BaseURL
	if useTestnet {
		baseURL = TestnetBaseURL
	}
	
	return &Client{
		APIKey:     apiKey,
		SecretKey:  secretKey,
		BaseURL:    baseURL,
		HTTPClient: &http.Client{Timeout: 30 * time.Second},
	}
}

// Balance represents account balance information
type Balance struct {
	AccountAlias       string `json:"accountAlias"`
	Asset              string `json:"asset"`
	Balance            string `json:"balance"`
	CrossWalletBalance string `json:"crossWalletBalance"`
	CrossUnPnl         string `json:"crossUnPnl"`
	AvailableBalance   string `json:"availableBalance"`
	MaxWithdrawAmount  string `json:"maxWithdrawAmount"`
	MarginAvailable    bool   `json:"marginAvailable"`
	UpdateTime         int64  `json:"updateTime"`
}

// AccountInfo represents account information
type AccountInfo struct {
	FeeTier                     int       `json:"feeTier"`
	CanTrade                    bool      `json:"canTrade"`
	CanDeposit                  bool      `json:"canDeposit"`
	CanWithdraw                 bool      `json:"canWithdraw"`
	UpdateTime                  int64     `json:"updateTime"`
	TotalInitialMargin          string    `json:"totalInitialMargin"`
	TotalMaintMargin            string    `json:"totalMaintMargin"`
	TotalWalletBalance          string    `json:"totalWalletBalance"`
	TotalUnrealizedProfit       string    `json:"totalUnrealizedProfit"`
	TotalMarginBalance          string    `json:"totalMarginBalance"`
	TotalPositionInitialMargin  string    `json:"totalPositionInitialMargin"`
	TotalOpenOrderInitialMargin string    `json:"totalOpenOrderInitialMargin"`
	TotalCrossWalletBalance     string    `json:"totalCrossWalletBalance"`
	TotalCrossUnPnl             string    `json:"totalCrossUnPnl"`
	AvailableBalance            string    `json:"availableBalance"`
	MaxWithdrawAmount           string    `json:"maxWithdrawAmount"`
	Assets                      []Balance `json:"assets"`
}

// generateSignature creates HMAC SHA256 signature
func (c *Client) generateSignature(params string) string {
	h := hmac.New(sha256.New, []byte(c.SecretKey))
	h.Write([]byte(params))
	return hex.EncodeToString(h.Sum(nil))
}

// makeRequest makes HTTP request to Binance API
func (c *Client) makeRequest(method, endpoint string, params url.Values) ([]byte, error) {
	// Add timestamp
	timestamp := strconv.FormatInt(time.Now().UnixMilli(), 10)
	params.Set("timestamp", timestamp)
	
	// Create query string
	queryString := params.Encode()
	
	// Generate signature
	signature := c.generateSignature(queryString)
	queryString += "&signature=" + signature
	
	// Create request URL
	requestURL := c.BaseURL + endpoint + "?" + queryString
	
	// Create HTTP request
	req, err := http.NewRequest(method, requestURL, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	
	// Add headers
	req.Header.Set("X-MBX-APIKEY", c.APIKey)
	req.Header.Set("Content-Type", "application/json")
	
	// Make request
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %w", err)
	}
	defer resp.Body.Close()
	
	// Read response
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}
	
	// Check status code
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API error (status %d): %s", resp.StatusCode, string(body))
	}
	
	return body, nil
}

// GetAccountInfo retrieves account information
func (c *Client) GetAccountInfo() (*AccountInfo, error) {
	params := url.Values{}
	
	body, err := c.makeRequest("GET", AccountInfoEndpoint, params)
	if err != nil {
		return nil, fmt.Errorf("failed to get account info: %w", err)
	}
	
	var accountInfo AccountInfo
	if err := json.Unmarshal(body, &accountInfo); err != nil {
		return nil, fmt.Errorf("failed to parse account info: %w", err)
	}
	
	return &accountInfo, nil
}

// GetBalance retrieves account balance
func (c *Client) GetBalance() ([]Balance, error) {
	params := url.Values{}
	
	body, err := c.makeRequest("GET", BalanceEndpoint, params)
	if err != nil {
		return nil, fmt.Errorf("failed to get balance: %w", err)
	}
	
	var balances []Balance
	if err := json.Unmarshal(body, &balances); err != nil {
		return nil, fmt.Errorf("failed to parse balance: %w", err)
	}
	
	return balances, nil
}

// GetUSDTBalance retrieves USDT balance specifically
func (c *Client) GetUSDTBalance() (*Balance, error) {
	balances, err := c.GetBalance()
	if err != nil {
		return nil, err
	}
	
	for _, balance := range balances {
		if balance.Asset == "USDT" {
			return &balance, nil
		}
	}
	
	return nil, fmt.Errorf("USDT balance not found")
}
