package orchestrator

import (
	"fmt"
	"log"
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