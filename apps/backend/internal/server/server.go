package server

import (
	"log/slog"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/kirillsobolev/soul-mirror/backend/internal/api"
	"github.com/kirillsobolev/soul-mirror/backend/internal/orchestrator"
	"github.com/kirillsobolev/soul-mirror/backend/internal/profile"
	"github.com/kirillsobolev/soul-mirror/backend/internal/tools"
)

type Server struct {
	handlers *api.Handlers
	port     string
	logger   *slog.Logger
	router   *gin.Engine
}

func New(orch orchestrator.Orchestrator, profileService profile.ProfileService, toolService tools.ToolService, logger *slog.Logger, environment, port string) *Server {
	handlers := api.NewHandlers(orch, profileService, toolService, logger, environment)
	
	// Set Gin mode based on environment
	if environment == "production" {
		gin.SetMode(gin.ReleaseMode)
	}
	
	router := gin.New()
	
	// Add middleware
	router.Use(gin.Logger())
	router.Use(gin.Recovery())
	
	// Configure CORS
	config := cors.DefaultConfig()
	config.AllowAllOrigins = true
	config.AllowMethods = []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}
	config.AllowHeaders = []string{"Origin", "Content-Type", "Content-Length", "Accept-Encoding", "X-CSRF-Token", "Authorization", "accept", "origin", "Cache-Control", "X-Requested-With"}
	router.Use(cors.New(config))
	
	return &Server{
		handlers: handlers,
		port:     port,
		logger:   logger,
		router:   router,
	}
}

func (s *Server) setupRoutes() {
	// Health endpoint
	s.router.GET("/health", s.handlers.HealthHandler)
	
	// Main endpoints
	s.router.GET("/process", s.handlers.ProcessHandler)
	s.router.GET("/profile", s.handlers.ProfileHandler)
	
	// API endpoints
	api := s.router.Group("/api")
	{
		api.GET("/tools", s.handlers.ToolsHandler)
		api.GET("/status", s.handlers.StatusHandler)
	}
}

func (s *Server) Start() error {
	s.setupRoutes()
	s.logger.Info("Server starting", slog.String("port", s.port))
	return s.router.Run(":" + s.port)
}