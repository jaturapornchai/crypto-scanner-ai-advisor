package analysis

import (
	"context"
	"fmt"
	"math"
	"sort"
	"strconv"
	"time"

	"github.com/adshao/go-binance/v2/futures"
)

// Kline represents a candlestick data point
type Kline struct {
	OpenTime  int64   `json:"openTime"`
	Open      float64 `json:"open"`
	High      float64 `json:"high"`
	Low       float64 `json:"low"`
	Close     float64 `json:"close"`
	Volume    float64 `json:"volume"`
	CloseTime int64   `json:"closeTime"`
	IsGreen   bool    `json:"isGreen"`
	IsRed     bool    `json:"isRed"`
}

// LinearRegressionChannel represents the channel data
type LinearRegressionChannel struct {
	UpperLine  float64 `json:"upperLine"`
	MiddleLine float64 `json:"middleLine"`
	LowerLine  float64 `json:"lowerLine"`
	Slope      float64 `json:"slope"`
	Deviation  float64 `json:"deviation"`
	TrendUp    bool    `json:"trendUp"`
	TrendDown  bool    `json:"trendDown"`
}

// BreakoutSignal represents a breakout detection result
type BreakoutSignal struct {
	Symbol       string    `json:"symbol"`
	Timestamp    time.Time `json:"timestamp"`
	Type         string    `json:"type"` // "UP_BREAKOUT", "DOWN_BREAKOUT", "RETEST_SUCCESS"
	Price        float64   `json:"price"`
	ChannelLevel float64   `json:"channelLevel"`
	Strength     int       `json:"strength"` // Number of previous candles that respected the level
	Description  string    `json:"description"`
	Confidence   float64   `json:"confidence"`
	RSI          float64   `json:"rsi"` // RSI value at signal time
}

// BreakoutInfo stores information about a recent breakout
type BreakoutInfo struct {
	BreakoutType string // "UP" or "DOWN"
	Price        float64
	Index        int
	Level        float64
}

// TechnicalAnalyzer handles technical analysis operations
type TechnicalAnalyzer struct {
	Length    int     // Linear regression length (default: 100)
	DevLength float64 // Deviation multiplier (default: 2.0)
}

// NewTechnicalAnalyzer creates a new technical analyzer
func NewTechnicalAnalyzer() *TechnicalAnalyzer {
	return &TechnicalAnalyzer{
		Length:    100,
		DevLength: 2.0,
	}
}

// GetKlineData retrieves historical kline data
func (ta *TechnicalAnalyzer) GetKlineData(client *futures.Client, symbol string, interval string, limit int) ([]*Kline, error) {
	klines, err := client.NewKlinesService().
		Symbol(symbol).
		Interval(interval).
		Limit(limit).
		Do(context.Background())

	if err != nil {
		return nil, fmt.Errorf("failed to get kline data: %w", err)
	}

	var result []*Kline
	for _, k := range klines {
		open, _ := strconv.ParseFloat(k.Open, 64)
		high, _ := strconv.ParseFloat(k.High, 64)
		low, _ := strconv.ParseFloat(k.Low, 64)
		close, _ := strconv.ParseFloat(k.Close, 64)
		volume, _ := strconv.ParseFloat(k.Volume, 64)

		kline := &Kline{
			OpenTime:  k.OpenTime,
			Open:      open,
			High:      high,
			Low:       low,
			Close:     close,
			Volume:    volume,
			CloseTime: k.CloseTime,
			IsGreen:   close > open,
			IsRed:     close < open,
		}
		result = append(result, kline)
	}

	return result, nil
}

// CalculateLinearRegressionChannel calculates the linear regression channel
func (ta *TechnicalAnalyzer) CalculateLinearRegressionChannel(prices []float64, length int) *LinearRegressionChannel {
	if len(prices) < length {
		return nil
	}

	// Get the last 'length' prices
	data := prices[len(prices)-length:]

	// Calculate linear regression
	slope, intercept := ta.linearRegression(data)

	// Calculate deviation
	dev := 0.0
	for i, price := range data {
		predicted := intercept + slope*float64(i)
		dev += math.Pow(price-predicted, 2)
	}
	dev = math.Sqrt(dev / float64(length))

	// Calculate channel lines
	currentX := float64(length - 1)
	currentMiddle := intercept + slope*currentX
	upperLine := currentMiddle + dev*ta.DevLength
	lowerLine := currentMiddle - dev*ta.DevLength

	return &LinearRegressionChannel{
		UpperLine:  upperLine,
		MiddleLine: currentMiddle,
		LowerLine:  lowerLine,
		Slope:      slope,
		Deviation:  dev,
		TrendUp:    slope > 0,
		TrendDown:  slope < 0,
	}
}

// linearRegression calculates slope and intercept for linear regression
func (ta *TechnicalAnalyzer) linearRegression(data []float64) (slope, intercept float64) {
	n := float64(len(data))
	sumX := 0.0
	sumY := 0.0
	sumXY := 0.0
	sumXX := 0.0

	for i, y := range data {
		x := float64(i)
		sumX += x
		sumY += y
		sumXY += x * y
		sumXX += x * x
	}

	slope = (n*sumXY - sumX*sumY) / (n*sumXX - sumX*sumX)
	intercept = (sumY - slope*sumX) / n

	return slope, intercept
}

// sum calculates the sum of a slice
func (ta *TechnicalAnalyzer) sum(data []float64) float64 {
	total := 0.0
	for _, v := range data {
		total += v
	}
	return total
}

// DetectBreakouts analyzes kline data for breakout patterns
func (ta *TechnicalAnalyzer) DetectBreakouts(klines []*Kline, symbol string) []*BreakoutSignal {
	if len(klines) < ta.Length+10 {
		return nil
	}

	var signals []*BreakoutSignal

	// Extract closing prices
	var closes []float64
	for _, k := range klines {
		closes = append(closes, k.Close)
	}

	// Calculate channel once for the entire dataset (excluding last 10 candles for prediction)
	analysisEnd := len(klines) - 10
	channel := ta.CalculateLinearRegressionChannel(closes[:analysisEnd], ta.Length)
	if channel == nil {
		return nil
	}

	// Analyze the last 10 candles for breakouts and retests
	for i := analysisEnd; i < len(klines); i++ {
		currentKline := klines[i]

		// Calculate RSI at current position
		currentRSI := ta.CalculateRSI(closes[:i+1], 14) // 14-period RSI

		// Check for breakouts with RSI filter
		if signal := ta.checkBreakout(currentKline, channel, symbol, i, klines); signal != nil {
			signal.RSI = currentRSI
			// Apply RSI filter
			if ta.RSIFilter(currentRSI, signal.Type) {
				signals = append(signals, signal)
			}
		}

		// Check for retests with proper validation and RSI filter
		if signal := ta.checkRetest(currentKline, channel, symbol, i, klines); signal != nil {
			signal.RSI = currentRSI
			// Apply RSI filter for retest signals
			retestType := signal.Type
			if signal.Type == "RETEST_SUCCESS" {
				// Determine if it's an upper or lower retest for RSI filtering
				if signal.Price > signal.ChannelLevel {
					retestType = "RETEST_SUCCESS_UP"
				} else {
					retestType = "RETEST_SUCCESS_DOWN"
				}
			}
			if ta.RSIFilter(currentRSI, retestType) {
				signals = append(signals, signal)
			}
		}
	}

	return signals
}

// checkBreakout detects breakout patterns
func (ta *TechnicalAnalyzer) checkBreakout(kline *Kline, channel *LinearRegressionChannel, symbol string, index int, klines []*Kline) *BreakoutSignal {
	// Minimum breakout threshold to avoid false signals
	minBreakoutThreshold := channel.Deviation * 0.1

	// UP BREAKOUT: Green candle closes above upper channel with sufficient margin
	if kline.IsGreen && kline.Close > channel.UpperLine+minBreakoutThreshold {
		// Check volume confirmation (if previous candle exists)
		volumeConfirmed := true
		if index > 0 {
			volumeConfirmed = kline.Volume > klines[index-1].Volume*1.1 // 10% volume increase
		}

		strength := ta.calculateSupport(klines, index, channel.UpperLine, false, 10)
		confidence := ta.calculateConfidence(strength, kline.Close-channel.UpperLine, channel.Deviation)

		// Volume confirmation bonus
		if volumeConfirmed {
			confidence = math.Min(confidence*1.1, 1.0)
		}

		// Strong green candle bonus (body > 70% of total range)
		candleBody := math.Abs(kline.Close - kline.Open)
		candleRange := kline.High - kline.Low
		if candleRange > 0 && candleBody/candleRange > 0.7 {
			confidence = math.Min(confidence*1.05, 1.0)
		}

		return &BreakoutSignal{
			Symbol:       symbol,
			Timestamp:    time.Unix(kline.OpenTime/1000, 0),
			Type:         "UP_BREAKOUT",
			Price:        kline.Close,
			ChannelLevel: channel.UpperLine,
			Strength:     strength,
			Description: fmt.Sprintf("Green candle broke above upper channel at %.4f (strength: %d, volume: %s)",
				channel.UpperLine, strength, func() string {
					if volumeConfirmed {
						return "confirmed"
					}
					return "weak"
				}()),
			Confidence: confidence,
		}
	}

	// DOWN BREAKOUT: Red candle closes below lower channel with sufficient margin
	if kline.IsRed && kline.Close < channel.LowerLine-minBreakoutThreshold {
		// Check volume confirmation
		volumeConfirmed := true
		if index > 0 {
			volumeConfirmed = kline.Volume > klines[index-1].Volume*1.1
		}

		strength := ta.calculateSupport(klines, index, channel.LowerLine, true, 10)
		confidence := ta.calculateConfidence(strength, channel.LowerLine-kline.Close, channel.Deviation)

		// Volume confirmation bonus
		if volumeConfirmed {
			confidence = math.Min(confidence*1.1, 1.0)
		}

		// Strong red candle bonus
		candleBody := math.Abs(kline.Close - kline.Open)
		candleRange := kline.High - kline.Low
		if candleRange > 0 && candleBody/candleRange > 0.7 {
			confidence = math.Min(confidence*1.05, 1.0)
		}

		return &BreakoutSignal{
			Symbol:       symbol,
			Timestamp:    time.Unix(kline.OpenTime/1000, 0),
			Type:         "DOWN_BREAKOUT",
			Price:        kline.Close,
			ChannelLevel: channel.LowerLine,
			Strength:     strength,
			Description: fmt.Sprintf("Red candle broke below lower channel at %.4f (strength: %d, volume: %s)",
				channel.LowerLine, strength, func() string {
					if volumeConfirmed {
						return "confirmed"
					}
					return "weak"
				}()),
			Confidence: confidence,
		}
	}

	return nil
}

// checkRetest detects successful retests with enhanced validation
func (ta *TechnicalAnalyzer) checkRetest(kline *Kline, channel *LinearRegressionChannel, symbol string, index int, klines []*Kline) *BreakoutSignal {
	tolerance := channel.Deviation * 0.15 // Reduced tolerance for more precise retests

	// Check if there was a previous breakout to retest (stricter criteria)
	breakoutInfo := ta.findRecentBreakout(klines, index, channel, 5)
	if breakoutInfo == nil {
		return nil
	}

	// RETEST OF UPPER LEVEL (after UP breakout)
	if breakoutInfo.BreakoutType == "UP" {
		// Price must touch the level and bounce successfully
		if kline.Low <= channel.UpperLine+tolerance && kline.Close > channel.UpperLine {
			// Validate it's actually a successful bounce
			bounceStrength := (kline.Close - kline.Low) / (kline.High - kline.Low)
			if bounceStrength < 0.6 { // Must close in upper 40% of candle range
				return nil
			}

			strength := ta.calculateRetestStrength(klines, index, channel.UpperLine, true, 10)
			confidence := 0.70 + (float64(strength)/10.0)*0.25 // Base 70% + strength bonus

			// Bonus for strong bounce
			if bounceStrength > 0.8 {
				confidence = math.Min(confidence*1.1, 1.0)
			}

			return &BreakoutSignal{
				Symbol:       symbol,
				Timestamp:    time.Unix(kline.OpenTime/1000, 0),
				Type:         "RETEST_SUCCESS",
				Price:        kline.Close,
				ChannelLevel: channel.UpperLine,
				Strength:     strength,
				Description: fmt.Sprintf("✅ Successful retest of upper channel support (%.4f) - Price bounced from %.4f to %.4f",
					channel.UpperLine, kline.Low, kline.Close),
				Confidence: math.Min(confidence, 1.0),
			}
		}

		// Failed retest
		if kline.Close < channel.UpperLine-tolerance {
			return &BreakoutSignal{
				Symbol:       symbol,
				Timestamp:    time.Unix(kline.OpenTime/1000, 0),
				Type:         "RETEST_FAILED",
				Price:        kline.Close,
				ChannelLevel: channel.UpperLine,
				Strength:     0,
				Description: fmt.Sprintf("❌ Failed retest of upper channel support (%.4f) - Price fell to %.4f",
					channel.UpperLine, kline.Close),
				Confidence: 0.8, // High confidence in failure
			}
		}
	}

	// RETEST OF LOWER LEVEL (after DOWN breakout)
	if breakoutInfo.BreakoutType == "DOWN" {
		// Price must touch the level and bounce successfully
		if kline.High >= channel.LowerLine-tolerance && kline.Close < channel.LowerLine {
			// Validate it's actually a successful rejection
			rejectionStrength := (kline.High - kline.Close) / (kline.High - kline.Low)
			if rejectionStrength < 0.6 { // Must close in lower 40% of candle range
				return nil
			}

			strength := ta.calculateRetestStrength(klines, index, channel.LowerLine, false, 10)
			confidence := 0.70 + (float64(strength)/10.0)*0.25 // Base 70% + strength bonus

			// Bonus for strong rejection
			if rejectionStrength > 0.8 {
				confidence = math.Min(confidence*1.1, 1.0)
			}

			return &BreakoutSignal{
				Symbol:       symbol,
				Timestamp:    time.Unix(kline.OpenTime/1000, 0),
				Type:         "RETEST_SUCCESS",
				Price:        kline.Close,
				ChannelLevel: channel.LowerLine,
				Strength:     strength,
				Description: fmt.Sprintf("✅ Successful retest of lower channel resistance (%.4f) - Price rejected from %.4f to %.4f",
					channel.LowerLine, kline.High, kline.Close),
				Confidence: math.Min(confidence, 1.0),
			}
		}

		// Failed retest
		if kline.Close > channel.LowerLine+tolerance {
			return &BreakoutSignal{
				Symbol:       symbol,
				Timestamp:    time.Unix(kline.OpenTime/1000, 0),
				Type:         "RETEST_FAILED",
				Price:        kline.Close,
				ChannelLevel: channel.LowerLine,
				Strength:     0,
				Description: fmt.Sprintf("❌ Failed retest of lower channel resistance (%.4f) - Price rose to %.4f",
					channel.LowerLine, kline.Close),
				Confidence: 0.8, // High confidence in failure
			}
		}
	}

	return nil
}

// checkStrongBreakout detects strong breakout patterns that may set up retests
func (ta *TechnicalAnalyzer) checkStrongBreakout(kline *Kline, channel *LinearRegressionChannel, symbol string, index int, klines []*Kline) *BreakoutSignal {
	breakoutThreshold := channel.Deviation * 0.5 // Must break by at least 50% of deviation

	// STRONG UP BREAKOUT: Candle closes significantly above upper channel
	if kline.Close > channel.UpperLine+breakoutThreshold {
		strength := ta.calculateSupport(klines, index, channel.UpperLine, false, 20)
		confidence := ta.calculateConfidence(strength, kline.Close-channel.UpperLine, channel.Deviation)

		// Boost confidence for strong breakouts
		confidence = math.Min(confidence*1.2, 1.0)

		return &BreakoutSignal{
			Symbol:       symbol,
			Timestamp:    time.Unix(kline.OpenTime/1000, 0),
			Type:         "UP_BREAKOUT",
			Price:        kline.Close,
			ChannelLevel: channel.UpperLine,
			Strength:     strength,
			Description:  fmt.Sprintf("Strong breakout above upper channel at %.4f (distance: %.2f%%)", channel.UpperLine, (kline.Close-channel.UpperLine)/channel.UpperLine*100),
			Confidence:   confidence,
		}
	}

	// STRONG DOWN BREAKOUT: Candle closes significantly below lower channel
	if kline.Close < channel.LowerLine-breakoutThreshold {
		strength := ta.calculateSupport(klines, index, channel.LowerLine, true, 20)
		confidence := ta.calculateConfidence(strength, channel.LowerLine-kline.Close, channel.Deviation)

		// Boost confidence for strong breakouts
		confidence = math.Min(confidence*1.2, 1.0)

		return &BreakoutSignal{
			Symbol:       symbol,
			Timestamp:    time.Unix(kline.OpenTime/1000, 0),
			Type:         "DOWN_BREAKOUT",
			Price:        kline.Close,
			ChannelLevel: channel.LowerLine,
			Strength:     strength,
			Description:  fmt.Sprintf("Strong breakout below lower channel at %.4f (distance: %.2f%%)", channel.LowerLine, (channel.LowerLine-kline.Close)/channel.LowerLine*100),
			Confidence:   confidence,
		}
	}

	return nil
}

// checkRecentBreakout checks if there was a recent breakout to validate retests
func (ta *TechnicalAnalyzer) checkRecentBreakout(klines []*Kline, currentIndex int, channel *LinearRegressionChannel, lookback int) bool {
	start := currentIndex - lookback
	if start < 0 {
		start = 0
	}

	for i := start; i < currentIndex; i++ {
		kline := klines[i]

		// Check for previous breakout above upper channel
		if kline.Close > channel.UpperLine {
			return true
		}

		// Check for previous breakout below lower channel
		if kline.Close < channel.LowerLine {
			return true
		}
	}

	return false
}

// findRecentBreakout finds the most recent breakout and returns its information
func (ta *TechnicalAnalyzer) findRecentBreakout(klines []*Kline, currentIndex int, channel *LinearRegressionChannel, lookback int) *BreakoutInfo {
	start := currentIndex - lookback
	if start < 0 {
		start = 0
	}

	minBreakoutThreshold := channel.Deviation * 0.1

	// Look for most recent breakout (search backwards)
	for i := currentIndex - 1; i >= start; i-- {
		kline := klines[i]

		// Check for UP breakout
		if kline.Close > channel.UpperLine+minBreakoutThreshold {
			return &BreakoutInfo{
				BreakoutType: "UP",
				Price:        kline.Close,
				Index:        i,
				Level:        channel.UpperLine,
			}
		}

		// Check for DOWN breakout
		if kline.Close < channel.LowerLine-minBreakoutThreshold {
			return &BreakoutInfo{
				BreakoutType: "DOWN",
				Price:        kline.Close,
				Index:        i,
				Level:        channel.LowerLine,
			}
		}
	}

	return nil
}

// calculateRetestStrength calculates the strength of a retest based on how price interacts with the level
func (ta *TechnicalAnalyzer) calculateRetestStrength(klines []*Kline, currentIndex int, level float64, isSupport bool, lookback int) int {
	strength := 0
	start := currentIndex - lookback
	if start < 0 {
		start = 0
	}

	tolerance := level * 0.005 // 0.5% tolerance

	for i := start; i < currentIndex; i++ {
		kline := klines[i]

		if isSupport {
			// For support retest, count how many times it held as support
			if kline.Low <= level+tolerance && kline.Close > level {
				strength++
			}
		} else {
			// For resistance retest, count how many times it held as resistance
			if kline.High >= level-tolerance && kline.Close < level {
				strength++
			}
		}
	}

	return strength
}

// calculateSupport counts how many previous candles respected the level
func (ta *TechnicalAnalyzer) calculateSupport(klines []*Kline, currentIndex int, level float64, isSupport bool, lookback int) int {
	count := 0
	start := currentIndex - lookback
	if start < 0 {
		start = 0
	}

	for i := start; i < currentIndex; i++ {
		if isSupport {
			// For support level, count candles that stayed above
			if klines[i].Low >= level {
				count++
			}
		} else {
			// For resistance level, count candles that stayed below
			if klines[i].High <= level {
				count++
			}
		}
	}

	return count
}

// calculateConfidence calculates breakout confidence based on various factors
func (ta *TechnicalAnalyzer) calculateConfidence(strength int, distance float64, deviation float64) float64 {
	// Base confidence from strength (0-1)
	strengthConfidence := float64(strength) / 10.0
	if strengthConfidence > 1.0 {
		strengthConfidence = 1.0
	}

	// Distance confidence (how far the breakout is)
	distanceConfidence := distance / deviation
	if distanceConfidence > 1.0 {
		distanceConfidence = 1.0
	}

	// Combined confidence
	confidence := (strengthConfidence + distanceConfidence) / 2.0
	if confidence > 1.0 {
		confidence = 1.0
	}

	return confidence
}

// CalculateRSI calculates Relative Strength Index
func (ta *TechnicalAnalyzer) CalculateRSI(prices []float64, period int) float64 {
	if len(prices) < period+1 {
		return 50.0 // Default neutral RSI
	}

	// Get the last period+1 prices to calculate gains/losses
	data := prices[len(prices)-period-1:]

	var gains, losses []float64

	// Calculate price changes
	for i := 1; i < len(data); i++ {
		change := data[i] - data[i-1]
		if change > 0 {
			gains = append(gains, change)
			losses = append(losses, 0)
		} else {
			gains = append(gains, 0)
			losses = append(losses, -change)
		}
	}

	// Calculate average gains and losses
	avgGain := ta.sum(gains) / float64(len(gains))
	avgLoss := ta.sum(losses) / float64(len(losses))

	if avgLoss == 0 {
		return 100.0 // No losses = maximum RSI
	}

	rs := avgGain / avgLoss
	rsi := 100 - (100 / (1 + rs))

	return rsi
}

// RSIFilter checks if RSI is suitable for LONG/SHORT signals
func (ta *TechnicalAnalyzer) RSIFilter(rsi float64, signalType string) bool {
	switch signalType {
	case "UP_BREAKOUT", "RETEST_SUCCESS_UP":
		// For LONG signals: RSI should not be extremely overbought
		// Allow RSI between 30-80 (avoid extreme overbought above 80)
		return rsi >= 30 && rsi <= 80
	case "DOWN_BREAKOUT", "RETEST_SUCCESS_DOWN":
		// For SHORT signals: RSI should not be extremely oversold
		// Allow RSI between 20-70 (avoid extreme oversold below 20)
		return rsi >= 20 && rsi <= 70
	default:
		return true // Default: allow all
	}
}

// AnalyzeSymbol performs complete breakout analysis for a symbol
func (ta *TechnicalAnalyzer) AnalyzeSymbol(client *futures.Client, symbol string) ([]*BreakoutSignal, error) {
	// Get 1h kline data (enough for analysis + history)
	klines, err := ta.GetKlineData(client, symbol, "1h", ta.Length+50)
	if err != nil {
		return nil, err
	}

	// Detect breakouts
	signals := ta.DetectBreakouts(klines, symbol)

	return signals, nil
}

// FormatSignals formats breakout signals for display
func (ta *TechnicalAnalyzer) FormatSignals(signals []*BreakoutSignal) string {
	if len(signals) == 0 {
		return "No breakout signals detected"
	}

	// Sort signals by timestamp (newest first)
	sort.Slice(signals, func(i, j int) bool {
		return signals[i].Timestamp.After(signals[j].Timestamp)
	})

	result := fmt.Sprintf("🎯 Found %d breakout signals:\n\n", len(signals))

	for i, signal := range signals {
		emoji := "📈"
		if signal.Type == "DOWN_BREAKOUT" {
			emoji = "📉"
		} else if signal.Type == "RETEST_SUCCESS" {
			emoji = "🔄"
		}

		result += fmt.Sprintf("%s %d. %s - %s\n", emoji, i+1, signal.Symbol, signal.Type)
		result += fmt.Sprintf("   Time: %s\n", signal.Timestamp.Format("2006-01-02 15:04:05"))
		result += fmt.Sprintf("   Price: %.4f | Level: %.4f\n", signal.Price, signal.ChannelLevel)
		result += fmt.Sprintf("   Strength: %d | Confidence: %.2f%% | RSI: %.1f\n", signal.Strength, signal.Confidence*100, signal.RSI)
		result += fmt.Sprintf("   %s\n\n", signal.Description)
	}

	return result
}

// BreakoutData represents breakout analysis result for AI
type BreakoutData struct {
	HasBreakout bool    `json:"has_breakout"`
	Direction   string  `json:"direction"` // "UP" or "DOWN" or "NEUTRAL"
	Confidence  float64 `json:"confidence"`
}

// CandleData represents candlestick data compatible with AI analysis
type CandleData struct {
	Timestamp int64   `json:"timestamp"`
	Open      float64 `json:"open"`
	High      float64 `json:"high"`
	Low       float64 `json:"low"`
	Close     float64 `json:"close"`
	Volume    float64 `json:"volume"`
}

// DetectBreakouts analyzes candlestick data for breakout patterns (utility function)
func DetectBreakouts(symbol string, candles []CandleData, period int, deviation float64) *BreakoutData {
	if len(candles) < period {
		return &BreakoutData{
			HasBreakout: false,
			Direction:   "NEUTRAL",
			Confidence:  0.0,
		}
	}

	// Convert CandleData to Kline format
	klines := make([]*Kline, len(candles))
	for i, candle := range candles {
		klines[i] = &Kline{
			OpenTime:  candle.Timestamp,
			Open:      candle.Open,
			High:      candle.High,
			Low:       candle.Low,
			Close:     candle.Close,
			Volume:    candle.Volume,
			CloseTime: candle.Timestamp + 3600000, // Add 1 hour in milliseconds
			IsGreen:   candle.Close > candle.Open,
			IsRed:     candle.Close < candle.Open,
		}
	}

	// Create analyzer and detect breakouts
	analyzer := NewTechnicalAnalyzer()
	signals := analyzer.DetectBreakouts(klines, symbol)

	// Analyze the most recent signals
	if len(signals) == 0 {
		return &BreakoutData{
			HasBreakout: false,
			Direction:   "NEUTRAL",
			Confidence:  0.0,
		}
	}

	// Get the most recent signal
	latestSignal := signals[len(signals)-1]

	var direction string
	hasBreakout := false

	switch latestSignal.Type {
	case "UP_BREAKOUT", "RETEST_SUCCESS":
		direction = "UP"
		hasBreakout = true
	case "DOWN_BREAKOUT", "RETEST_FAILED":
		direction = "DOWN"
		hasBreakout = true
	default:
		direction = "NEUTRAL"
		hasBreakout = false
	}

	return &BreakoutData{
		HasBreakout: hasBreakout,
		Direction:   direction,
		Confidence:  latestSignal.Confidence,
	}
}
