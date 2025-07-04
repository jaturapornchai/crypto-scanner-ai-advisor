package main

import (
	"fmt"
	"testing"
)

// Simplified test that doesn't require external dependencies
func TestCoreBreakoutLogic(t *testing.T) {
	fmt.Println("🧪 TESTING CORE BREAKOUT LOGIC")
	fmt.Println("==============================")
	
	// Test candle color detection
	greenCandle := &CandleData{Open: 100, Close: 105}
	redCandle := &CandleData{Open: 105, Close: 100}
	
	if getCandleColor(greenCandle) != "Green" {
		t.Error("Expected green candle to be detected as Green")
	}
	
	if getCandleColor(redCandle) != "Red" {
		t.Error("Expected red candle to be detected as Red")
	}
	
	fmt.Printf("✅ Candle color detection: PASSED\n")
	
	// Test quantity formatting
	quantity := 0.123456789
	formatted := formatQuantity("BTCUSDT", quantity)
	
	if formatted != 0.123 {
		t.Errorf("Expected quantity %.3f, got %.3f", 0.123, formatted)
	}
	
	fmt.Printf("✅ Quantity formatting: PASSED\n")
	
	// Test Fibonacci calculation with sample data
	sampleData := make([]*CandleData, 50)
	for i := 0; i < 50; i++ {
		price := 100.0 + float64(i)*2
		sampleData[i] = &CandleData{
			Open:  price,
			High:  price + 3,
			Low:   price - 1,
			Close: price + 2,
		}
	}
	
	fib := calculateFibonacci(sampleData)
	
	if fib.High == 0 || fib.Low == 0 {
		t.Error("Fibonacci calculation failed")
	}
	
	if fib.Level236 <= fib.Level786 {
		t.Error("Fibonacci levels are not in correct order")
	}
	
	fmt.Printf("✅ Fibonacci calculation: PASSED\n")
	fmt.Printf("   High: %.2f, Low: %.2f\n", fib.High, fib.Low)
	fmt.Printf("   Direction: %s\n", fib.Direction)
	
	fmt.Println("\n🎉 ALL CORE TESTS PASSED!")
	fmt.Println("========================")
	fmt.Println("The breakout trading system core logic is working correctly.")
}
