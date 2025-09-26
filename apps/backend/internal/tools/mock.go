package tools

import (
	"fmt"
	"log"
)

type MockTool struct {
	name        string
	description string
}

func NewMockTool(name string) Tool {
	return &MockTool{
		name:        name,
		description: fmt.Sprintf("Mock tool for %s operations", name),
	}
}

func (m *MockTool) Execute(input string) (string, error) {
	log.Printf("MockTool '%s': Executing with input: %s", m.name, input)
	response := fmt.Sprintf("Mock %s: %s", m.name, input)
	return response, nil
}

func (m *MockTool) Name() string {
	return m.name
}

func (m *MockTool) Description() string {
	return m.description
}

type MockToolService struct {
	tools map[string]Tool
}

func NewMockToolService() ToolService {
	return &MockToolService{
		tools: map[string]Tool{
			"echo": NewMockTool("echo"),
			"test": NewMockTool("test"),
		},
	}
}

func (m *MockToolService) GetTool(name string) Tool {
	tool, exists := m.tools[name]
	if !exists {
		log.Printf("MockToolService: Tool '%s' not found", name)
		return nil
	}
	log.Printf("MockToolService: Retrieved tool: %s", name)
	return tool
}

func (m *MockToolService) RegisterTool(tool Tool) {
	m.tools[tool.Name()] = tool
	log.Printf("MockToolService: Registered tool: %s", tool.Name())
}

func (m *MockToolService) ListTools() []Tool {
	tools := make([]Tool, 0, len(m.tools))
	for _, tool := range m.tools {
		tools = append(tools, tool)
	}
	return tools
}