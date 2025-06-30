package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) > 1 && os.Args[1] == "trade" {
		runTrader()
	} else {
		fmt.Println("Usage: go run . trade")
		fmt.Println("This will run the crypto trading scanner with AI analysis")
	}
}
