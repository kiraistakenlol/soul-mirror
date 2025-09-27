package handlers

import (
	"log/slog"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/kirillsobolev/soul-mirror/backend/internal/tools"
)

type ToolsHandler struct {
	toolService tools.ToolService
	logger      *slog.Logger
}

func NewToolsHandler(toolSvc tools.ToolService, logger *slog.Logger) *ToolsHandler {
	return &ToolsHandler{
		toolService: toolSvc,
		logger:      logger,
	}
}

func (h *ToolsHandler) Handle(c *gin.Context) {
	h.logger.Debug("Tools list requested")
	
	toolsList := h.toolService.ListTools()
	toolInfos := make([]ToolInfo, len(toolsList))
	
	for i, tool := range toolsList {
		toolInfos[i] = ToolInfo{
			Name:        tool.Name(),
			Description: tool.Description(),
		}
	}

	response := ToolsResponse{
		Tools: toolInfos,
		Count: len(toolInfos),
	}

	h.logger.Info("Tools list generated", slog.Int("tools_count", len(toolInfos)))
	c.JSON(http.StatusOK, response)
}