# Use official Golang image as base
FROM golang:1.24-alpine AS builder

# Install necessary packages
RUN apk add --no-cache git ca-certificates tzdata

# Set working directory
WORKDIR /app

# Copy go mod files first for better caching
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o tread2 .

# Start a new stage from scratch for smaller image
FROM alpine:latest

# Install ca-certificates for HTTPS requests and timezone data
RUN apk --no-cache add ca-certificates tzdata

# Set timezone to Bangkok
ENV TZ=Asia/Bangkok

WORKDIR /root/

# Copy the binary from builder stage
COPY --from=builder /app/tread2 .

# Make the binary executable
RUN chmod +x ./tread2

# Expose port for future web interface
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgrep tread2 || exit 1

# Run the application
CMD ["./tread2", "trade"]
