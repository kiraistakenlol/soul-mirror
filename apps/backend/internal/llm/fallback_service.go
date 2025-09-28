// fallback_service provides a fallback implementation when no LLM API key is available.
package llm

import (
	"log"
)

type fallbackService struct{}

func (s *fallbackService) SelectTools(userInput string, availableTools []ToolDescriptor) ([]ToolSelection, error) {
	log.Printf("⚠️  Fallback: No LLM available for tool selection")
	return []ToolSelection{}, nil
}

func (s *fallbackService) UpdateProfile(userInput string, currentProfile string, extractionTargets []ExtractionTarget) (*ProfileExtractionResponse, error) {
	log.Printf("⚠️  Fallback: No LLM available for profile update")
	return &ProfileExtractionResponse{
		UpdatedProfile:   currentProfile,
		ExtractedTargets: []ExtractionResult{},
	}, nil
}
