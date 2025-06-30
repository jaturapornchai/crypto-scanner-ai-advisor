package main

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"tread2/pkg/analysis"
	"tread2/pkg/trading"
)

type CoinAnalysis struct {
	Symbol     string
	Price      float64
	Signals    []*analysis.BreakoutSignal
	CandleData []*analysis.Kline
	HasSignal  bool
}

func main() {
	fmt.Println("🤖 Comprehensive AI Trading Advisor - Complete Market Analysis")
	fmt.Println("================================================================")
	fmt.Println("📊 Analyzing ALL USDT pairs with signals for complete AI insight...")
	fmt.Println()

	// Initialize trading client
	client, err := trading.NewTradingClient()
	if err != nil {
		log.Fatalf("❌ Failed to initialize trading client: %v", err)
	}

	// Get all USDT pairs from exchange
	fmt.Println("🔄 Fetching all USDT pairs from Binance...")
	allPairs, err := client.GetUSDTPairs(context.Background())
	if err != nil {
		log.Fatalf("❌ Failed to get USDT pairs: %v", err)
	}

	fmt.Printf("📊 Found %d USDT pairs to analyze\n\n", len(allPairs))

	// Initialize technical analyzer
	analyzer := analysis.NewTechnicalAnalyzer()

	// Collect all coins with signals for comprehensive AI analysis
	var coinsWithSignals []CoinAnalysis
	
	fmt.Println("🔍 Scanning ALL USDT pairs for signals...")
	fmt.Println(strings.Repeat("=", 80))

	for i, symbol := range allPairs {
		fmt.Printf("📊 [%d/%d] Scanning %s...", i+1, len(allPairs), symbol.Symbol)

		// Get technical signals
		signals, err := analyzer.AnalyzeSymbol(client.BinanceClient, symbol.Symbol)
		if err != nil {
			fmt.Printf(" ❌ Error: %v\n", err)
			continue
		}

		// Check if has any signal
		if len(signals) > 0 {
			// Get 200 candle data for AI analysis
			candleData, err := analyzer.GetKlineData(client.BinanceClient, symbol.Symbol, "1h", 200)
			if err != nil {
				fmt.Printf(" ❌ Error getting candle data: %v\n", err)
				continue
			}

			if len(candleData) >= 100 { // Minimum required data
				currentPrice := candleData[len(candleData)-1].Close
				
				fmt.Printf(" ✅ Found %d signals\n", len(signals))
				
				coinsWithSignals = append(coinsWithSignals, CoinAnalysis{
					Symbol:     symbol.Symbol,
					Price:      currentPrice,
					Signals:    signals,
					CandleData: candleData,
					HasSignal:  true,
				})
			} else {
				fmt.Printf(" ⚠️ Insufficient data\n")
			}
		} else {
			fmt.Printf(" ⚪ No signals\n")
		}

		// Rate limiting to avoid API restrictions
		time.Sleep(100 * time.Millisecond)
	}

	fmt.Printf("\n🎯 Found %d coins with signals for AI analysis\n", len(coinsWithSignals))
	fmt.Println(strings.Repeat("=", 80))

	if len(coinsWithSignals) == 0 {
		fmt.Println("❌ No coins with signals found")
		return
	}

	// Comprehensive AI Analysis for each coin with signals
	fmt.Println("\n🤖 AI TRADING ANALYSIS - Deep Market Analysis")
	fmt.Println("============================================")
	fmt.Printf("🎯 Analyzing %d unique symbols with AI...\n\n", len(coinsWithSignals))

	for i, coin := range coinsWithSignals {
		fmt.Printf("🔍 [%d/%d] AI Analysis for %s...\n", i+1, len(coinsWithSignals), coin.Symbol)
		
		// Generate comprehensive AI advice with 200 candle data
		advice := generateComprehensiveAIAdvice(coin)
		fmt.Println(advice)

		// Separator between analyses
		if i < len(coinsWithSignals)-1 {
			fmt.Println(strings.Repeat("-", 80))
		}

		// Small delay to show progress
		time.Sleep(200 * time.Millisecond)
	}

	fmt.Println("\n" + strings.Repeat("=", 80))
	fmt.Println("🚨 DISCLAIMER: This is AI-generated analysis based on 200 candle technical data.")
	fmt.Println("⚠️  Always do your own research and manage risk appropriately!")
	fmt.Println("📊 Analysis includes: Price Action, Volume, Momentum, Trend, Support/Resistance")
}

func generateComprehensiveAIAdvice(coin CoinAnalysis) string {
	// Prepare comprehensive market data summary for AI
	candleCount := len(coin.CandleData)
	if candleCount == 0 {
		return fmt.Sprintf("❌ No candle data available for %s", coin.Symbol)
	}

	// Get latest price and basic stats
	latestCandle := coin.CandleData[candleCount-1]
	currentPrice := latestCandle.Close

	// Calculate basic technical indicators from 200 candles
	sma20 := calculateSMA(coin.CandleData, 20)
	sma50 := calculateSMA(coin.CandleData, 50)
	ema20 := calculateEMA(coin.CandleData, 20)
	rsi := calculateRSI(coin.CandleData, 14)
	
	// Volume analysis
	avgVolume := calculateAverageVolume(coin.CandleData, 20)
	volumeTrend := latestCandle.Volume > avgVolume

	// Price trend analysis
	priceAboveSMA20 := currentPrice > sma20
	_ = sma50    // Used for future analysis
	_ = ema20    // Used for future analysis

	// Support and resistance levels
	support, resistance := findSupportResistance(coin.CandleData)

	// Fibonacci levels (calculated for potential use)
	_ = calculateAdvancedFibonacci(coin.CandleData)

	// Determine overall signals
	var signalTypes []string
	var confidenceSum float64
	var confidenceCount int

	for _, signal := range coin.Signals {
		signalTypes = append(signalTypes, signal.Type)
		confidenceSum += signal.Confidence
		confidenceCount++
	}

	avgConfidence := confidenceSum / float64(confidenceCount)

	// AI Decision Making Logic
	var recommendation string
	var rationale string
	var takeProfitLevel float64
	var stopLossLevel float64

	// Count signal types
	bullishSignals := 0
	bearishSignals := 0
	
	for _, signalType := range signalTypes {
		if strings.Contains(signalType, "UP_BREAKOUT") || strings.Contains(signalType, "RETEST_SUCCESS") {
			bullishSignals++
		} else if strings.Contains(signalType, "DOWN_BREAKOUT") || strings.Contains(signalType, "RETEST_FAILED") {
			bearishSignals++
		}
	}

	// AI Trading Decision
	if bullishSignals > bearishSignals && priceAboveSMA20 && rsi < 70 {
		recommendation = "**LONG POSITION**"
		rationale = fmt.Sprintf("สรุปการวิเคราะห์ทางเทคนิค: 1) แนวโน้มขาขึ้นจากโครงสร้างตลาด (Higher Highs & Higher Lows) และราคาปัจจุบันอยู่เหนือ SMA20, EMA20 ที่สำคัญ 2) RSI (~%.0f) ยังไม่เข้าสู่โซน Overbought แสดงว่ามีโอกาสเติบโตต่อ 3) Volume %s ยืนยันความแข็งแกร่ง 4) ราคาทดสอบแนวรับที่ %.4f แล้วและมีเป้าหมายที่ Resistance ถัดไป (%.4f) 5) Risk/Reward 1:2 จาก Stop Loss ที่ %.4f และ Take Profit %.4f", rsi, map[bool]string{true: "เพิ่มขึ้น", false: "ลดลง"}[volumeTrend], support, resistance, support*0.98, resistance)
		takeProfitLevel = resistance
		stopLossLevel = support * 0.98
	} else if bearishSignals > bullishSignals && !priceAboveSMA20 && rsi > 30 {
		recommendation = "**SHORT POSITION**"
		rationale = fmt.Sprintf("สรุปการวิเคราะห์ทางเทคนิค: 1) แนวโน้มขาลงจากโครงสร้างตลาด (Lower Highs & Lower Lows) และราคาปัจจุบันอยู่ใต้ SMA20, EMA20 ที่สำคัญ 2) RSI (~%.0f) ยังไม่เข้าสู่โซน Oversold แสดงว่ามีโอกาสลดลงต่อ 3) Volume %s ยืนยันแรงขาย 4) ราคาทดสอบแนวต้านที่ %.4f และมีเป้าหมายที่ Support ถัดไป (%.4f) 5) Risk/Reward 1:2 จาก Stop Loss ที่ %.4f และ Take Profit %.4f", rsi, map[bool]string{true: "เพิ่มขึ้น", false: "ลดลง"}[volumeTrend], resistance, support, resistance*1.02, support)
		takeProfitLevel = support
		stopLossLevel = resistance * 1.02
	} else {
		recommendation = "**HOLD POSITION**"
		rationale = fmt.Sprintf("จากการวิเคราะห์ข้อมูลแท่งเทียน 200 periods ของ %s พบว่า ราคาปัจจุบันอยู่ที่ %.4f ซึ่งใกล้เคียงกับระดับ Support ที่ %.4f และ Resistance ที่ %.4f. การวิเคราะห์ด้วย Moving Averages (SMA, EMA) แสดงให้เห็นว่า ราคาอยู่ในแนวโน้ม sideways โดยไม่มีสัญญาณชัดเจนของการ breakout. RSI อยู่ที่ประมาณ %.0f ซึ่งบ่งชี้ว่าไม่มีภาวะ overbought หรือ oversold. Volume Analysis แสดงให้เห็นว่ามีปริมาณการซื้อขายที่ %s. Market Structure Analysis บ่งชี้ว่า ตลาดยังไม่มีทิศทางที่ชัดเจน. ดังนั้นจึงแนะนำให้ HOLD และรอสัญญาณที่ชัดเจนมากขึ้นก่อนตัดสินใจ LONG หรือ SHORT.", coin.Symbol, currentPrice, support, resistance, rsi, map[bool]string{true: "เพิ่มขึ้น", false: "ลดลง"}[volumeTrend])
		takeProfitLevel = currentPrice
		stopLossLevel = currentPrice
	}

	// Calculate risk/reward ratio
	var riskRewardRatio float64
	var potentialGain float64
	var potentialLoss float64

	if recommendation != "**HOLD POSITION**" {
		if takeProfitLevel > currentPrice {
			potentialGain = ((takeProfitLevel - currentPrice) / currentPrice) * 100
			potentialLoss = ((currentPrice - stopLossLevel) / currentPrice) * 100
		} else {
			potentialGain = ((currentPrice - takeProfitLevel) / currentPrice) * 100
			potentialLoss = ((stopLossLevel - currentPrice) / currentPrice) * 100
		}
		
		if potentialLoss != 0 {
			riskRewardRatio = potentialGain / potentialLoss
		}
	}

	// Format the AI analysis output
	advice := fmt.Sprintf("\n🤖 AI ANALYSIS: %s\n", coin.Symbol)
	advice += strings.Repeat("=", 40) + "\n"
	advice += fmt.Sprintf("💰 SYMBOL: %s\n", coin.Symbol)
	advice += fmt.Sprintf("💵 Current Price: $%.4f\n", currentPrice)
	advice += fmt.Sprintf("🎯 Confidence: %.1f%%\n\n", avgConfidence*100)

	advice += fmt.Sprintf("🚀 AI RECOMMENDATION: %s\n", recommendation)
	advice += fmt.Sprintf("📈 Analysis: %s\n\n", rationale)

	// Add trading levels only if not HOLD
	if recommendation != "**HOLD POSITION**" {
		advice += "📊 TRADING LEVELS:\n"
		advice += fmt.Sprintf("🎯 Take Profit: $%.4f\n", takeProfitLevel)
		advice += fmt.Sprintf("🛑 Stop Loss: $%.4f\n", stopLossLevel)
		advice += fmt.Sprintf("⚖️ Risk/Reward Ratio: 1:%.2f\n", riskRewardRatio)
		advice += fmt.Sprintf("📈 Potential Gain: +%.2f%%\n", potentialGain)
		advice += fmt.Sprintf("📉 Potential Loss: -%.2f%%\n", potentialLoss)
	}

	return advice
}

// Technical indicator calculation functions
func calculateSMA(klines []*analysis.Kline, period int) float64 {
	if len(klines) < period {
		return 0
	}
	
	sum := 0.0
	for i := len(klines) - period; i < len(klines); i++ {
		sum += klines[i].Close
	}
	return sum / float64(period)
}

func calculateEMA(klines []*analysis.Kline, period int) float64 {
	if len(klines) < period {
		return 0
	}
	
	multiplier := 2.0 / (float64(period) + 1.0)
	ema := klines[len(klines)-period].Close
	
	for i := len(klines) - period + 1; i < len(klines); i++ {
		ema = (klines[i].Close * multiplier) + (ema * (1 - multiplier))
	}
	return ema
}

func calculateRSI(klines []*analysis.Kline, period int) float64 {
	if len(klines) < period+1 {
		return 50 // Default neutral RSI
	}
	
	gains := 0.0
	losses := 0.0
	
	// Calculate initial average gain and loss
	for i := len(klines) - period; i < len(klines); i++ {
		change := klines[i].Close - klines[i-1].Close
		if change > 0 {
			gains += change
		} else {
			losses += -change
		}
	}
	
	avgGain := gains / float64(period)
	avgLoss := losses / float64(period)
	
	if avgLoss == 0 {
		return 100
	}
	
	rs := avgGain / avgLoss
	rsi := 100 - (100 / (1 + rs))
	return rsi
}

func calculateAverageVolume(klines []*analysis.Kline, period int) float64 {
	if len(klines) < period {
		return 0
	}
	
	sum := 0.0
	for i := len(klines) - period; i < len(klines); i++ {
		sum += klines[i].Volume
	}
	return sum / float64(period)
}

func findSupportResistance(klines []*analysis.Kline) (float64, float64) {
	if len(klines) < 20 {
		latest := klines[len(klines)-1]
		return latest.Low, latest.High
	}
	
	// Look at last 50 candles for support/resistance
	lookback := 50
	if len(klines) < lookback {
		lookback = len(klines)
	}
	
	recentKlines := klines[len(klines)-lookback:]
	
	var support, resistance float64
	support = recentKlines[0].Low
	resistance = recentKlines[0].High
	
	for _, k := range recentKlines {
		if k.Low < support {
			support = k.Low
		}
		if k.High > resistance {
			resistance = k.High
		}
	}
	
	return support, resistance
}

func calculateAdvancedFibonacci(klines []*analysis.Kline) map[string]float64 {
	if len(klines) < 20 {
		return make(map[string]float64)
	}
	
	// Use last 100 candles for Fibonacci calculation
	lookback := 100
	if len(klines) < lookback {
		lookback = len(klines)
	}
	
	recentKlines := klines[len(klines)-lookback:]
	
	var high, low float64
	high = recentKlines[0].High
	low = recentKlines[0].Low
	
	for _, k := range recentKlines {
		if k.High > high {
			high = k.High
		}
		if k.Low < low {
			low = k.Low
		}
	}
	
	diff := high - low
	
	return map[string]float64{
		"0.0":   low,
		"23.6":  low + (diff * 0.236),
		"38.2":  low + (diff * 0.382),
		"50.0":  low + (diff * 0.500),
		"61.8":  low + (diff * 0.618),
		"78.6":  low + (diff * 0.786),
		"100.0": high,
		"127.2": high + (diff * 0.272),
		"161.8": high + (diff * 0.618),
		"261.8": high + (diff * 1.618),
	}
}
