package status

import (
	"log/slog"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/kirillsobolev/soul-mirror/backend/internal/tools"
)

type Handler struct {
	toolService tools.ToolService
	logger      *slog.Logger
	environment string
}

func NewHandler(toolSvc tools.ToolService, logger *slog.Logger, environment string) *Handler {
	return &Handler{
		toolService: toolSvc,
		logger:      logger,
		environment: environment,
	}
}

func (h *Handler) Handle(c *gin.Context) {
	h.logger.Debug("Status check requested")

	toolsCount := len(h.toolService.ListTools())

	response := ServerStatusResponse{
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
