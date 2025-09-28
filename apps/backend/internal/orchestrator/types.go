package orchestrator

import (
	"time"

	"github.com/kirillsobolev/soul-mirror/backend/internal/llm"
)

type ProcessResponse struct {
	Input  string        `json:"input"`
	Result ProcessResult `json:"result"`
}

type ProcessResult struct {
	FinalResponse     string            `json:"final_response"`
	ProcessingDetails ProcessingDetails `json:"processing_details"`
}

type ProcessingDetails struct {
	ToolSelectionResult ToolSelectionResult `json:"tool_selection_result"`
	ToolExecutions      []ToolExecution     `json:"tool_executions"`
	ProfileUpdate       ProfileUpdate       `json:"profile_update"`
}

type ToolSelectionResult struct {
	ToolsConsidered int                 `json:"tools_considered"`
	ToolsSelected   []llm.ToolSelection `json:"tools_selected"`
	ProcessingTime  string              `json:"processing_time"`
}

type ToolExecution struct {
	ToolName      string `json:"tool_name"`
	Input         string `json:"input"`
	Output        string `json:"output"`
	ExecutionTime string `json:"execution_time"`
	Status        string `json:"status"`
	Error         string `json:"error,omitempty"`
}

type ProfileUpdate struct {
	ChangesMade         string                     `json:"changes_made"`
	ProfileLengthBefore int                        `json:"profile_length_before"`
	ProfileLengthAfter  int                        `json:"profile_length_after"`
	ExtractedTargets    []llm.ExtractionResult `json:"extracted_targets"`
	ProcessingTime      string                     `json:"processing_time"`
	Success             bool                       `json:"success"`
}

type ProcessMetadata struct {
	TotalProcessingTime string    `json:"total_processing_time"`
	Timestamp           time.Time `json:"timestamp"`
	ToolsExecuted       int       `json:"tools_executed"`
	LLMCallsMade        int       `json:"llm_calls_made"`
	Environment         string    `json:"environment"`
}
