package main

import (
	"log"

	"github.com/kirillsobolev/soul-mirror/backend/internal/config"
	"github.com/kirillsobolev/soul-mirror/backend/internal/llm"
	"github.com/kirillsobolev/soul-mirror/backend/internal/logging"
	"github.com/kirillsobolev/soul-mirror/backend/internal/orchestrator"
	"github.com/kirillsobolev/soul-mirror/backend/internal/profile"
	"github.com/kirillsobolev/soul-mirror/backend/internal/server"
	"github.com/kirillsobolev/soul-mirror/backend/internal/tools"
)

func main() {
	log.Println("Initializing Soul Mirror backend...")

	cfg := config.Load()
	log.Printf("✓ Configuration loaded (environment: %s)", cfg.Environment)
	if cfg.HasAnthropicKey() {
		log.Println("✓ Anthropic API key found")
	} else {
		log.Println("⚠️  No Anthropic API key - running in fallback mode")
	}

	logger := logging.InitLogger(cfg.Environment)
	log.Println("✓ Structured logger initialized")

	toolService := tools.NewToolService()
	toolsList := toolService.ListTools()
	log.Println("✓ Tool service initialized with tools:")
	for _, tool := range toolsList {
		log.Printf("  - %s: %s", tool.Name(), tool.Description())
	}

	profileService := profile.NewService()
	log.Println("✓ Profile service initialized")

	llmService := llm.NewService(cfg)
	log.Println("✓ LLM service initialized")

	orch := orchestrator.New(toolService, profileService, llmService)
	log.Println("✓ Orchestrator initialized")

	srv := server.New(orch, profileService, toolService, logger, cfg.Environment, cfg.Port)
	log.Println("✓ Server initialized")

	log.Println("🚀 Starting Soul Mirror backend server...")
	if err := srv.Start(); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}