package profile

import (
	"log/slog"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/kirillsobolev/soul-mirror/backend/internal/profile"
)

type Handler struct {
	profileService profile.ProfileService
	logger         *slog.Logger
}

func NewHandler(profileSvc profile.ProfileService, logger *slog.Logger) *Handler {
	return &Handler{
		profileService: profileSvc,
		logger:         logger,
	}
}

func (h *Handler) Handle(c *gin.Context) {
	h.logger.Debug("Profile requested")
	
	profile, err := h.profileService.Get()
	if err != nil {
		h.logger.Error("Failed to get profile", slog.String("error", err.Error()))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get profile"})
		return
	}

	response := Response{Profile: profile}
	h.logger.Debug("Profile retrieved", slog.Int("profile_length", len(profile)))
	c.JSON(http.StatusOK, response)
}