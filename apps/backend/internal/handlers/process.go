// handlers provides HTTP handlers for the Soul Mirror API
package handlers

import (
	"log/slog"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/kirillsobolev/soul-mirror/backend/internal/orchestrator"
)

type ProcessHandler struct {
	orchestrator orchestrator.Orchestrator
	logger       *slog.Logger
}

func NewProcessHandler(orch orchestrator.Orchestrator, logger *slog.Logger) *ProcessHandler {
	return &ProcessHandler{
		orchestrator: orch,
		logger:       logger,
	}
}

func (h *ProcessHandler) Handle(c *gin.Context) {
	startTime := time.Now()
	input := c.Query("input")
	
	h.logger.Info("Processing user input", 
		slog.String("user_input", input),
		slog.String("method", c.Request.Method),
		slog.String("path", c.Request.URL.Path))

	if input == "" {
		h.logger.Warn("Empty input received")
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing 'input' parameter"})
		return
	}

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
		slog.String("response", response.Result.FinalResponse),
		slog.Duration("processing_time", processingTime))

	c.JSON(http.StatusOK, response)
}