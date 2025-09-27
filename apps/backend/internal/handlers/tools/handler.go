package tools

import (
	"log/slog"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/kirillsobolev/soul-mirror/backend/internal/tools"
)

type Handler struct {
	toolService tools.ToolService
	logger      *slog.Logger
}

func NewHandler(toolSvc tools.ToolService, logger *slog.Logger) *Handler {
	return &Handler{
		toolService: toolSvc,
		logger:      logger,
	}
}

func (h *Handler) Handle(c *gin.Context) {
	h.logger.Debug("Tools list requested")
	
	toolsList := h.toolService.ListTools()
	toolInfos := make([]ToolInfo, len(toolsList))
	
	for i, tool := range toolsList {
		toolInfos[i] = ToolInfo{
			Name:        tool.Name(),
			Description: tool.Description(),
		}
	}

	response := Response{
		Tools: toolInfos,
		Count: len(toolInfos),
	}

	h.logger.Info("Tools list generated", slog.Int("tools_count", len(toolInfos)))
	c.JSON(http.StatusOK, response)
}