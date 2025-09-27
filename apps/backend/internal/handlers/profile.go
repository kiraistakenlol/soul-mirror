package handlers

import (
	"log/slog"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/kirillsobolev/soul-mirror/backend/internal/profile"
)

type ProfileHandler struct {
	profileService profile.ProfileService
	logger         *slog.Logger
}

func NewProfileHandler(profileSvc profile.ProfileService, logger *slog.Logger) *ProfileHandler {
	return &ProfileHandler{
		profileService: profileSvc,
		logger:         logger,
	}
}

func (h *ProfileHandler) Handle(c *gin.Context) {
	h.logger.Debug("Profile requested")
	
	profile, err := h.profileService.Get()
	if err != nil {
		h.logger.Error("Failed to get profile", slog.String("error", err.Error()))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get profile"})
		return
	}

	response := ProfileResponse{Profile: profile}
	h.logger.Debug("Profile retrieved", slog.Int("profile_length", len(profile)))
	c.JSON(http.StatusOK, response)
}