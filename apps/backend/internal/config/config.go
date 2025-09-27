// config loads and provides application configuration from environment variables.
package config

import (
	"log"
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	AnthropicAPIKey string
	OpenAIAPIKey    string
	LLMProvider     string
	Port            string
	Environment     string
}

func Load() *Config {
	if err := godotenv.Load(); err != nil {
		log.Printf("No .env file found, using environment variables")
	}

	return &Config{
		AnthropicAPIKey: os.Getenv("ANTHROPIC_API_KEY"),
		OpenAIAPIKey:    os.Getenv("OPENAI_API_KEY"),
		LLMProvider:     getEnv("LLM_PROVIDER", "anthropic"),
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

func (c *Config) HasOpenAIKey() bool {
	return c.OpenAIAPIKey != ""
}

func (c *Config) HasLLMKey() bool {
	switch c.LLMProvider {
	case "openai":
		return c.HasOpenAIKey()
	case "anthropic":
		return c.HasAnthropicKey()
	default:
		return false
	}
}