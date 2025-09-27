package status

type ServerStatusResponse struct {
	Status       string `json:"status"`
	LLMAvailable bool   `json:"llm_available"`
	Environment  string `json:"environment"`
	ToolsCount   int    `json:"tools_count"`
	Version      string `json:"version"`
}
