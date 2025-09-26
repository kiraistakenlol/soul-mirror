package llm

import (
	"log"
	"strings"
)

type MockLLMService struct{}

func NewMockService() LLMService {
	return &MockLLMService{}
}

func (m *MockLLMService) SelectTools(userInput string, availableTools []ToolDescriptor) ([]ToolSelection, error) {
	log.Printf("MockLLMService: Selecting tools for input: %s", userInput)
	
	// Simple mock logic - select based on keywords
	lowerInput := strings.ToLower(userInput)
	var selections []ToolSelection
	
	for _, tool := range availableTools {
		if tool.Name == "echo" && strings.Contains(lowerInput, "echo") {
			selection := ToolSelection{
				ToolName: tool.Name,
				Reason:   "Input contains 'echo' keyword - direct match",
			}
			selections = append(selections, selection)
			log.Printf("MockLLMService: Selected tool: %s (keyword match)", tool.Name)
			break
		}
	}
	
	// If no keyword match, default to first available tool
	if len(selections) == 0 && len(availableTools) > 0 {
		selection := ToolSelection{
			ToolName: availableTools[0].Name,
			Reason:   "No specific keywords detected - using default tool for general processing",
		}
		selections = append(selections, selection)
		log.Printf("MockLLMService: Selected default tool: %s", availableTools[0].Name)
	}
	
	if len(selections) == 0 {
		log.Printf("MockLLMService: No tools available")
	}
	
	return selections, nil
}

func (m *MockLLMService) ProcessText(input string) (string, error) {
	log.Printf("MockLLMService: Processing text: %s", input)
	response := "Mock LLM response: " + input
	log.Printf("MockLLMService: Generated response: %s", response)
	return response, nil
}