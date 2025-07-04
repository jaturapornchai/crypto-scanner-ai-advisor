package main

import (
	"testing"
)

// TestBreakoutSignalDetection tests the breakout signal detection logic
func TestBreakoutSignalDetection(t *testing.T) {
	// Create test candle data
	candleData := []*CandleData{
		// Previous candles (setup)
		{Open: 100, High: 105, Low: 95, Close: 102, Volume: 1000},
		{Open: 102, High: 107, Low: 98, Close: 104, Volume: 1100},
		{Open: 104, High: 109, Low: 101, Close: 106, Volume: 1200},
		// More candles for S/R calculation
		{Open: 106, High: 111, Low: 103, Close: 108, Volume: 1300},
		{Open: 108, High: 113, Low: 105, Close: 110, Volume: 1400},
		{Open: 110, High: 115, Low: 107, Close: 112, Volume: 1500},
		{Open: 112, High: 117, Low: 109, Close: 114, Volume: 1600},
		{Open: 114, High: 119, Low: 111, Close: 116, Volume: 1700},
		{Open: 116, High: 121, Low: 113, Close: 118, Volume: 1800},
		{Open: 118, High: 123, Low: 115, Close: 120, Volume: 1900},
		{Open: 120, High: 125, Low: 117, Close: 122, Volume: 2000},
		{Open: 122, High: 127, Low: 119, Close: 124, Volume: 2100},
		{Open: 124, High: 129, Low: 121, Close: 126, Volume: 2200},
		{Open: 126, High: 131, Low: 123, Close: 128, Volume: 2300},
		{Open: 128, High: 133, Low: 125, Close: 130, Volume: 2400},
		{Open: 130, High: 135, Low: 127, Close: 132, Volume: 2500},
		{Open: 132, High: 137, Low: 129, Close: 134, Volume: 2600},
		{Open: 134, High: 139, Low: 131, Close: 136, Volume: 2700},
		{Open: 136, High: 141, Low: 133, Close: 138, Volume: 2800},
		{Open: 138, High: 143, Low: 135, Close: 140, Volume: 2900},
		// Add more candles to reach minimum requirement
		{Open: 140, High: 145, Low: 137, Close: 142, Volume: 3000},
		{Open: 142, High: 147, Low: 139, Close: 144, Volume: 3100},
		{Open: 144, High: 149, Low: 141, Close: 146, Volume: 3200},
		{Open: 146, High: 151, Low: 143, Close: 148, Volume: 3300},
		{Open: 148, High: 153, Low: 145, Close: 150, Volume: 3400},
		{Open: 150, High: 155, Low: 147, Close: 152, Volume: 3500},
		{Open: 152, High: 157, Low: 149, Close: 154, Volume: 3600},
		{Open: 154, High: 159, Low: 151, Close: 156, Volume: 3700},
		{Open: 156, High: 161, Low: 153, Close: 158, Volume: 3800},
		{Open: 158, High: 163, Low: 155, Close: 160, Volume: 3900},
		{Open: 160, High: 165, Low: 157, Close: 162, Volume: 4000},
		{Open: 162, High: 167, Low: 159, Close: 164, Volume: 4100},
		{Open: 164, High: 169, Low: 161, Close: 166, Volume: 4200},
		{Open: 166, High: 171, Low: 163, Close: 168, Volume: 4300},
		{Open: 168, High: 173, Low: 165, Close: 170, Volume: 4400},
		{Open: 170, High: 175, Low: 167, Close: 172, Volume: 4500},
		{Open: 172, High: 177, Low: 169, Close: 174, Volume: 4600},
		{Open: 174, High: 179, Low: 171, Close: 176, Volume: 4700},
		{Open: 176, High: 181, Low: 173, Close: 178, Volume: 4800},
		{Open: 178, High: 183, Low: 175, Close: 180, Volume: 4900},
		{Open: 180, High: 185, Low: 177, Close: 182, Volume: 5000},
		{Open: 182, High: 187, Low: 179, Close: 184, Volume: 5100},
		{Open: 184, High: 189, Low: 181, Close: 186, Volume: 5200},
		{Open: 186, High: 191, Low: 183, Close: 188, Volume: 5300},
		{Open: 188, High: 193, Low: 185, Close: 190, Volume: 5400},
		{Open: 190, High: 195, Low: 187, Close: 192, Volume: 5500},
		{Open: 192, High: 197, Low: 189, Close: 194, Volume: 5600},
		{Open: 194, High: 199, Low: 191, Close: 196, Volume: 5700},
		{Open: 196, High: 201, Low: 193, Close: 198, Volume: 5800},
		{Open: 198, High: 203, Low: 195, Close: 200, Volume: 5900},
		// Previous candle: green above support (say support is around 195)
		{Open: 198, High: 202, Low: 196, Close: 200, Volume: 6000}, // Green candle above support
		// Current candle: breaks below support  
		{Open: 200, High: 201, Low: 193, Close: 194, Volume: 6100}, // Breaks below support
	}

	// Test the breakout signal analysis
	signal, err := analyzeBreakoutSignal(candleData, "TESTUSDT")
	if err != nil {
		t.Fatalf("Failed to analyze breakout signal: %v", err)
	}

	if signal == nil {
		t.Fatal("Expected a breakout signal, got nil")
	}

	t.Logf("Breakout Signal: %+v", signal)
	t.Logf("Support Level: %.2f", signal.SupportLevel)
	t.Logf("Resistance Level: %.2f", signal.ResistanceLevel)
	t.Logf("Signal Type: %s", signal.Signal)
	t.Logf("Breakout Type: %s", signal.BreakoutType)
}

// TestSupportResistanceLevels tests the support and resistance calculation
func TestSupportResistanceLevels(t *testing.T) {
	// Create test candle data with clear support/resistance
	candleData := make([]*CandleData, 60)
	for i := 0; i < 60; i++ {
		// Create some oscillating price data with clear levels
		base := 100.0
		variation := 10.0 * float64(i%10) / 10.0
		
		candleData[i] = &CandleData{
			Open:   base + variation,
			High:   base + variation + 2,
			Low:    base + variation - 2,
			Close:  base + variation + 1,
			Volume: 1000,
		}
	}

	support, resistance := calculateSupportResistanceLevels(candleData)
	
	if support == 0 && resistance == 0 {
		t.Error("Expected non-zero support and resistance levels")
	}
	
	t.Logf("Calculated Support: %.2f", support)
	t.Logf("Calculated Resistance: %.2f", resistance)
	
	if resistance <= support {
		t.Error("Resistance should be higher than support")
	}
}

// TestFibonacciCalculation tests the Fibonacci calculation
func TestFibonacciCalculation(t *testing.T) {
	// Create test candle data
	candleData := make([]*CandleData, 50)
	for i := 0; i < 50; i++ {
		// Create uptrending data
		price := 100.0 + float64(i)*2
		candleData[i] = &CandleData{
			Open:   price,
			High:   price + 3,
			Low:    price - 1,
			Close:  price + 2,
			Volume: 1000,
		}
	}

	fibonacci := calculateFibonacci(candleData)
	
	if fibonacci.High == 0 || fibonacci.Low == 0 {
		t.Error("Expected non-zero Fibonacci high and low values")
	}
	
	t.Logf("Fibonacci Levels: High=%.2f, Low=%.2f", fibonacci.High, fibonacci.Low)
	t.Logf("23.6%%: %.2f", fibonacci.Level236)
	t.Logf("38.2%%: %.2f", fibonacci.Level382)
	t.Logf("50.0%%: %.2f", fibonacci.Level500)
	t.Logf("61.8%%: %.2f", fibonacci.Level618)
	t.Logf("78.6%%: %.2f", fibonacci.Level786)
	t.Logf("Direction: %s", fibonacci.Direction)
	
	// Verify that Fibonacci levels are in correct order
	if fibonacci.Level236 < fibonacci.Level382 {
		t.Error("Fibonacci 23.6% should be higher than 38.2%")
	}
	if fibonacci.Level382 < fibonacci.Level500 {
		t.Error("Fibonacci 38.2% should be higher than 50.0%")
	}
}
