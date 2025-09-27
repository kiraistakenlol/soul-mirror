package llm

type ToolDescriptor struct {
	Name        string
	Description string
}

type ToolSelection struct {
	ToolName string
	Reason   string
}