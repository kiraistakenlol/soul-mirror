package tools

type ToolInfo struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

type Response struct {
	Tools []ToolInfo `json:"tools"`
	Count int        `json:"count"`
}