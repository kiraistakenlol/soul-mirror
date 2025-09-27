package tools

import (
	"fmt"
	"log"
)

type Tool interface {
	Execute(input string) (string, error)
	Name() string
	Description() string
}

type ToolService interface {
	GetTool(name string) Tool
	RegisterTool(tool Tool)
	ListTools() []Tool
}

type toolService struct {
	tools map[string]Tool
}

func NewToolService() ToolService {
	s := &toolService{
		tools: make(map[string]Tool),
	}
	
	s.RegisterTool(&EchoTool{})
	s.RegisterTool(NewTimeTool())
	return s
}

func (s *toolService) GetTool(name string) Tool {
	tool, exists := s.tools[name]
	if !exists {
		log.Printf("Tool '%s' not found", name)
		return nil
	}
	log.Printf("Retrieved tool: %s", name)
	return tool
}

func (s *toolService) RegisterTool(tool Tool) {
	s.tools[tool.Name()] = tool
	log.Printf("Registered tool: %s", tool.Name())
}

func (s *toolService) ListTools() []Tool {
	tools := make([]Tool, 0, len(s.tools))
	for _, tool := range s.tools {
		tools = append(tools, tool)
	}
	return tools
}

type EchoTool struct{}

func (t *EchoTool) Execute(input string) (string, error) {
	log.Printf("EchoTool: Executing with input: %s", input)
	response := fmt.Sprintf("Echo: %s", input)
	return response, nil
}

func (t *EchoTool) Name() string {
	return "echo"
}

func (t *EchoTool) Description() string {
	return "Echoes back the input with a prefix. Useful for testing and simple responses."
}