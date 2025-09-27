// server configures and runs the HTTP server with routing and middleware.
package server

import (
	"log/slog"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/kirillsobolev/soul-mirror/backend/internal/handlers"
	"github.com/kirillsobolev/soul-mirror/backend/internal/orchestrator"
	profileService "github.com/kirillsobolev/soul-mirror/backend/internal/profile"
	toolsService "github.com/kirillsobolev/soul-mirror/backend/internal/tools"
)

type Server struct {
	processHandler *handlers.ProcessHandler
	profileHandler *handlers.ProfileHandler
	toolsHandler   *handlers.ToolsHandler
	statusHandler  *handlers.StatusHandler
	port           string
	logger         *slog.Logger
	router         *gin.Engine
}

func New(orch orchestrator.Orchestrator, profileSvc profileService.ProfileService, toolSvc toolsService.ToolService, logger *slog.Logger, environment, port string) *Server {

	router := gin.New()

	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	config := cors.DefaultConfig()
	config.AllowAllOrigins = true
	config.AllowMethods = []string{"*"}
	config.AllowHeaders = []string{"*"}
	router.Use(cors.New(config))

	return &Server{
		processHandler: handlers.NewProcessHandler(orch, logger),
		profileHandler: handlers.NewProfileHandler(profileSvc, logger),
		toolsHandler:   handlers.NewToolsHandler(toolSvc, logger),
		statusHandler:  handlers.NewStatusHandler(toolSvc, logger, environment),
		port:           port,
		logger:         logger,
		router:         router,
	}
}

func (s *Server) setupRoutes() {
	api := s.router.Group("/api")
	{
		api.GET("/status", s.statusHandler.Handle)
		api.GET("/process", s.processHandler.Handle)
		api.GET("/profile", s.profileHandler.Handle)
		api.GET("/tools", s.toolsHandler.Handle)
	}
}

func (s *Server) Start() error {
	s.setupRoutes()
	s.logger.Info("Server starting", slog.String("port", s.port))
	return s.router.Run(":" + s.port)
}
