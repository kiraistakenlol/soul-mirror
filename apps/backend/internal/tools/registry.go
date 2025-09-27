// tools provides a registry for managing and executing available system tools.
package tools

import (
	"log"
)

type Tool interface {
	Execute(input string, context Context) (string, error)
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

	s.RegisterTool(NewTimeTool())
	s.RegisterTool(NewRandomTool())
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
