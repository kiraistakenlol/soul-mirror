package llm

type ToolDescriptor struct {
	Name        string
	Description string
}

type ToolSelection struct {
	ToolName string
	Reason   string
}

type ExtractionTarget struct {
	Name        string
	Description string
}

type ExtractionResult struct {
	TargetName string
	Content    string
	Found      bool
}

type ProfileExtractionResponse struct {
	UpdatedProfile   string
	ExtractedTargets []ExtractionResult
}