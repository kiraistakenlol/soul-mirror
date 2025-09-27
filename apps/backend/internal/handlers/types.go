package handlers

import "github.com/kirillsobolev/soul-mirror/backend/internal/types"

// Process endpoint types
type ProcessRequest struct {
	Input string `json:"input" form:"input" binding:"required"`
}

type ProcessResponse = types.ProcessResponse

// Profile endpoint types
type ProfileResponse struct {
	Profile string `json:"profile"`
}

// Tools endpoint types
type ToolInfo struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

type ToolsResponse struct {
	Tools []ToolInfo `json:"tools"`
	Count int        `json:"count"`
}

// Status endpoint types
type StatusResponse struct {
	Status       string `json:"status"`
	LLMAvailable bool   `json:"llm_available"`
	Environment  string `json:"environment"`
	ToolsCount   int    `json:"tools_count"`
	Version      string `json:"version"`
}