package types

import "time"

type ProcessResponse struct {
	Input  string        `json:"input"`
	Result ProcessResult `json:"result"`
}

type ProcessResult struct {
	FinalResponse     string            `json:"final_response"`
	ProcessingDetails ProcessingDetails `json:"processing_details"`
	Metadata          ProcessMetadata   `json:"metadata"`
}

type ProcessingDetails struct {
	LLMAnalysis    LLMAnalysisResult `json:"llm_analysis"`
	ToolExecutions []ToolExecution   `json:"tool_executions"`
	ProfileUpdate  ProfileUpdate     `json:"profile_update"`
}

type LLMAnalysisResult struct {
	ToolsConsidered int             `json:"tools_considered"`
	ToolsSelected   []ToolSelection `json:"tools_selected"`
	ProcessingTime  string          `json:"processing_time"`
	UsedFallback    bool            `json:"used_fallback"`
}

type ToolSelection struct {
	ToolName string `json:"tool_name"`
	Reason   string `json:"reason"`
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
	ChangesMade         string `json:"changes_made"`
	ProfileLengthBefore int    `json:"profile_length_before"`
	ProfileLengthAfter  int    `json:"profile_length_after"`
	ProcessingTime      string `json:"processing_time"`
	Success             bool   `json:"success"`
}

type ProcessMetadata struct {
	TotalProcessingTime string    `json:"total_processing_time"`
	Timestamp           time.Time `json:"timestamp"`
	ToolsExecuted       int       `json:"tools_executed"`
	LLMCallsMade        int       `json:"llm_calls_made"`
	Environment         string    `json:"environment"`
}

type ToolsResponse struct {
	Tools []ToolInfo `json:"tools"`
	Count int        `json:"count"`
}

type ToolInfo struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

type StatusResponse struct {
	Status       string `json:"status"`
	LLMAvailable bool   `json:"llm_available"`
	Environment  string `json:"environment"`
	ToolsCount   int    `json:"tools_count"`
	Version      string `json:"version"`
}