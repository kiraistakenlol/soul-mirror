package orchestrator

import (
	"fmt"
	"log"
	"time"

	"github.com/kirillsobolev/soul-mirror/backend/internal/types"
)

type MockOrchestrator struct{}

func NewMock() Orchestrator {
	return &MockOrchestrator{}
}

func (m *MockOrchestrator) ProcessInput(input string) (string, error) {
	log.Printf("MockOrchestrator: Processing input: %s", input)
	response := fmt.Sprintf("Mock processed: %s", input)
	log.Printf("MockOrchestrator: Generated response: %s", response)
	return response, nil
}

func (m *MockOrchestrator) ProcessInputDetailed(input string) (*types.ProcessResponse, error) {
	log.Printf("MockOrchestrator: Processing detailed input: %s", input)
	response := fmt.Sprintf("Mock processed: %s", input)
	
	return &types.ProcessResponse{
		Input: input,
		Result: types.ProcessResult{
			FinalResponse: response,
			ProcessingDetails: types.ProcessingDetails{
				LLMAnalysis: types.LLMAnalysisResult{
					ToolsConsidered: 1,
					ToolsSelected:   []types.ToolSelection{},
					ProcessingTime:  "1ms",
					UsedFallback:    true,
				},
				ToolExecutions: []types.ToolExecution{},
				ProfileUpdate: types.ProfileUpdate{
					ChangesMade:         "Mock profile update",
					ProfileLengthBefore: 0,
					ProfileLengthAfter:  0,
					ProcessingTime:      "1ms",
					Success:             true,
				},
			},
			Metadata: types.ProcessMetadata{
				TotalProcessingTime: "2ms",
				Timestamp:           time.Now(),
				ToolsExecuted:       0,
				LLMCallsMade:        0,
				Environment:         "mock",
			},
		},
	}, nil
}