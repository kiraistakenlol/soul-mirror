package config

import (
	"log"
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	AnthropicAPIKey string
	Port            string
	Environment     string
}

func Load() *Config {
	// Load .env file if it exists (ignore error for production)
	if err := godotenv.Load(); err != nil {
		log.Printf("No .env file found, using environment variables")
	}

	return &Config{
		AnthropicAPIKey: os.Getenv("ANTHROPIC_API_KEY"),
		Port:            getEnv("PORT", "8080"),
		Environment:     getEnv("ENVIRONMENT", "development"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func (c *Config) IsProduction() bool {
	return c.Environment == "production"
}

func (c *Config) HasAnthropicKey() bool {
	return c.AnthropicAPIKey != ""
}