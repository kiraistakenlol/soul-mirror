package api

import (
	"log/slog"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/kirillsobolev/soul-mirror/backend/internal/orchestrator"
	"github.com/kirillsobolev/soul-mirror/backend/internal/profile"
	"github.com/kirillsobolev/soul-mirror/backend/internal/tools"
	"github.com/kirillsobolev/soul-mirror/backend/internal/types"
)

type Handlers struct {
	orchestrator   orchestrator.Orchestrator
	profileService profile.ProfileService
	toolService    tools.ToolService
	logger         *slog.Logger
	environment    string
}

func NewHandlers(orch orchestrator.Orchestrator, profileSvc profile.ProfileService, toolSvc tools.ToolService, logger *slog.Logger, environment string) *Handlers {
	return &Handlers{
		orchestrator:   orch,
		profileService: profileSvc,
		toolService:    toolSvc,
		logger:         logger,
		environment:    environment,
	}
}

func (h *Handlers) ProcessHandler(c *gin.Context) {
	startTime := time.Now()
	input := c.Query("input")
	detailed := c.Query("detailed") == "true"
	
	h.logger.Info("Processing user input", 
		slog.String("user_input", input),
		slog.String("method", c.Request.Method),
		slog.String("path", c.Request.URL.Path),
		slog.Bool("detailed", detailed))

	if input == "" {
		h.logger.Warn("Empty input received")
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing 'input' parameter"})
		return
	}

	if detailed {
		response, err := h.orchestrator.ProcessInputDetailed(input)
		if err != nil {
			h.logger.Error("Detailed processing failed",
				slog.String("error", err.Error()),
				slog.String("user_input", input))
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Processing failed"})
			return
		}

		processingTime := time.Since(startTime)
		h.logger.Info("Detailed processing completed",
			slog.String("response", response.Result.FinalResponse),
			slog.Duration("processing_time", processingTime))

		c.JSON(http.StatusOK, response)
	} else {
		response, err := h.orchestrator.ProcessInput(input)
		if err != nil {
			h.logger.Error("Processing failed",
				slog.String("error", err.Error()),
				slog.String("user_input", input))
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Processing failed"})
			return
		}

		processingTime := time.Since(startTime)
		h.logger.Info("Processing completed",
			slog.String("response", response),
			slog.Duration("processing_time", processingTime))

		c.String(http.StatusOK, response)
	}
}

func (h *Handlers) ProfileHandler(c *gin.Context) {
	h.logger.Debug("Profile requested")
	
	profile, err := h.profileService.Get()
	if err != nil {
		h.logger.Error("Failed to get profile", slog.String("error", err.Error()))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get profile"})
		return
	}

	h.logger.Debug("Profile retrieved", slog.Int("profile_length", len(profile)))
	c.String(http.StatusOK, profile)
}

func (h *Handlers) ToolsHandler(c *gin.Context) {
	h.logger.Debug("Tools list requested")
	
	toolsList := h.toolService.ListTools()
	toolInfos := make([]types.ToolInfo, len(toolsList))
	
	for i, tool := range toolsList {
		toolInfos[i] = types.ToolInfo{
			Name:        tool.Name(),
			Description: tool.Description(),
		}
	}

	response := types.ToolsResponse{
		Tools: toolInfos,
		Count: len(toolInfos),
	}

	h.logger.Info("Tools list generated", slog.Int("tools_count", len(toolInfos)))
	c.JSON(http.StatusOK, response)
}

func (h *Handlers) StatusHandler(c *gin.Context) {
	h.logger.Debug("Status check requested")
	
	toolsCount := len(h.toolService.ListTools())
	
	response := types.StatusResponse{
		Status:       "healthy",
		LLMAvailable: true, // TODO: implement actual LLM health check
		Environment:  h.environment,
		ToolsCount:   toolsCount,
		Version:      "stage-3",
	}

	h.logger.Info("Status check completed", 
		slog.String("status", response.Status),
		slog.Int("tools_count", toolsCount))
	
	c.JSON(http.StatusOK, response)
}

func (h *Handlers) HealthHandler(c *gin.Context) {
	h.logger.Debug("Health check requested")
	c.String(http.StatusOK, "OK")
}