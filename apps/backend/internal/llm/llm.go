package llm

import (
	"log"
)

type ToolDescriptor struct {
	Name        string
	Description string
}

type ToolSelection struct {
	ToolName string
	Reason   string
}

type LLMService interface {
	SelectTools(userInput string, availableTools []ToolDescriptor) ([]ToolSelection, error)
	ProcessText(input string) (string, error)
}

type service struct{}

func NewService() LLMService {
	return &service{}
}

func (s *service) SelectTools(userInput string, availableTools []ToolDescriptor) ([]ToolSelection, error) {
	log.Printf("LLMService: Selecting tools for input: %s", userInput)
	log.Printf("LLMService: Available tools:")
	for _, tool := range availableTools {
		log.Printf("  - %s: %s", tool.Name, tool.Description)
	}

	// For MVP, select first available tool with reasoning
	// In real implementation, this would use LLM to analyze input and select best tools
	var selections []ToolSelection
	
	if len(availableTools) > 0 {
		selection := ToolSelection{
			ToolName: availableTools[0].Name,
			Reason:   "Default tool selection for MVP - would use LLM analysis in production",
		}
		selections = append(selections, selection)
		log.Printf("LLMService: Selected tools: %v", selections)
	}

	if len(selections) == 0 {
		log.Printf("LLMService: No tools selected")
	}
	
	return selections, nil
}

func (s *service) ProcessText(input string) (string, error) {
	log.Printf("LLMService: Processing text: %s", input)
	
	// For MVP, just return a simple processed version
	// In real implementation, this would use LLM for text processing
	response := "LLM processed: " + input
	log.Printf("LLMService: Generated response: %s", response)
	return response, nil
}