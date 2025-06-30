# Go parameters
GOCMD=go
GOBUILD=$(GOCMD) build
GOCLEAN=$(GOCMD) clean
GOTEST=$(GOCMD) test
GOGET=$(GOCMD) get
BINARY_NAME=tread2
BINARY_UNIX=$(BINARY_NAME)_unix

# Default target
all: test build

# Build the application
build:
	$(GOBUILD) -o $(BINARY_NAME).exe -v ./...

# Test the application
test:
	$(GOTEST) -v ./...

# Clean build files
clean:
	$(GOCLEAN)
	del /Q $(BINARY_NAME).exe 2>nul || true

# Run the application
run:
	$(GOBUILD) -o $(BINARY_NAME).exe -v ./...
	./$(BINARY_NAME).exe

# Install dependencies
deps:
	$(GOGET) -v -t -d ./...

# Format code
fmt:
	go fmt ./...

# Lint code (requires golangci-lint)
lint:
	golangci-lint run

# Build for different platforms
build-linux:
	set CGO_ENABLED=0& set GOOS=linux& set GOARCH=amd64& $(GOBUILD) -o $(BINARY_UNIX) -v

build-windows:
	set CGO_ENABLED=0& set GOOS=windows& set GOARCH=amd64& $(GOBUILD) -o $(BINARY_NAME).exe -v

# Specific application runs
balance:
	$(GOCMD) run cmd/balance/main.go

pairs:
	$(GOCMD) run cmd/pairs/main.go

scanner:
	$(GOCMD) run cmd/scanner/main.go

ai-advisor:
	$(GOCMD) run cmd/ai-advisor/main.go

# NEW: Comprehensive AI Advisor that analyzes ALL coins with signals
comprehensive-ai:
	$(GOCMD) run cmd/comprehensive-ai-advisor/main.go

breakout:
	$(GOCMD) run cmd/breakout/main.go $(SYMBOL)

demo:
	$(GOCMD) run cmd/demo/main.go

# Run Auto Trader Bot (Automated Trading)
auto-trader:
	@echo "⚠️  WARNING: This will execute REAL trades!"
	@echo "🔥 Make sure you're using TESTNET environment!"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read
	$(GOCMD) run cmd/auto-trader/main.go

# Help
help:
	@echo Available targets:
	@echo   build            - Build the application
	@echo   test             - Run tests
	@echo   clean            - Clean build files
	@echo   run              - Build and run the application
	@echo   deps             - Install dependencies
	@echo   fmt              - Format code
	@echo   lint             - Lint code (requires golangci-lint)
	@echo   build-linux      - Build for Linux
	@echo   build-windows    - Build for Windows
	@echo   balance          - Check account balance
	@echo   pairs            - List trading pairs
	@echo   scanner          - Run breakout scanner
	@echo   ai-advisor       - Run AI advisor (20 random coins)
	@echo   comprehensive-ai - Run comprehensive AI advisor (ALL coins with signals)
	@echo   breakout         - Analyze specific symbol (use SYMBOL=BTCUSDT)
	@echo   demo             - Run demo
	@echo   auto-trader      - Run Auto Trader Bot (REAL trades!)
	@echo   help             - Show this help

.PHONY: all build test clean run deps fmt lint build-linux build-windows balance pairs scanner ai-advisor comprehensive-ai breakout demo auto-trader help
