package config

import (
	"encoding/json"
	"fmt"
	"os"
)

// AppConfig represents application configuration
type AppConfig struct {
	Name        string `json:"name"`
	Version     string `json:"version"`
	Environment string `json:"environment"`
	Port        int    `json:"port"`
	Debug       bool   `json:"debug"`
}

// DefaultConfig returns default configuration
func DefaultConfig() *AppConfig {
	return &AppConfig{
		Name:        "Tread2",
		Version:     "1.0.0",
		Environment: "development",
		Port:        8080,
		Debug:       true,
	}
}

// LoadConfig loads configuration from a JSON file
func LoadConfig(filename string) (*AppConfig, error) {
	config := DefaultConfig()

	file, err := os.Open(filename)
	if err != nil {
		// If file doesn't exist, return default config
		if os.IsNotExist(err) {
			return config, nil
		}
		return nil, fmt.Errorf("failed to open config file: %w", err)
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	if err := decoder.Decode(config); err != nil {
		return nil, fmt.Errorf("failed to decode config: %w", err)
	}

	return config, nil
}

// SaveConfig saves configuration to a JSON file
func (c *AppConfig) SaveConfig(filename string) error {
	file, err := os.Create(filename)
	if err != nil {
		return fmt.Errorf("failed to create config file: %w", err)
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(c); err != nil {
		return fmt.Errorf("failed to encode config: %w", err)
	}

	return nil
}

// String returns string representation of config
func (c *AppConfig) String() string {
	return fmt.Sprintf("App: %s v%s (%s) - Port: %d, Debug: %v",
		c.Name, c.Version, c.Environment, c.Port, c.Debug)
}
