package orchestrator

import (
	"fmt"
	"log"

	"github.com/kirillsobolev/soul-mirror/backend/internal/llm"
	"github.com/kirillsobolev/soul-mirror/backend/internal/profile"
	"github.com/kirillsobolev/soul-mirror/backend/internal/tools"
)

type Orchestrator interface {
	ProcessInput(input string) (string, error)
}

type orchestrator struct {
	toolService    tools.ToolService
	profileService profile.ProfileService
	llmService     llm.LLMService
}

func New(toolService tools.ToolService, profileService profile.ProfileService, llmService llm.LLMService) Orchestrator {
	return &orchestrator{
		toolService:    toolService,
		profileService: profileService,
		llmService:     llmService,
	}
}

func (o *orchestrator) ProcessInput(input string) (string, error) {
	log.Printf("Orchestrator: Processing input: %s", input)

	// Get available tools and convert to descriptors for LLM
	toolsList := o.toolService.ListTools()
	toolDescriptors := make([]llm.ToolDescriptor, len(toolsList))
	for i, tool := range toolsList {
		toolDescriptors[i] = llm.ToolDescriptor{
			Name:        tool.Name(),
			Description: tool.Description(),
		}
	}

	// Let LLM select the best tools for this input
	toolSelections, err := o.llmService.SelectTools(input, toolDescriptors)
	if err != nil {
		return "", fmt.Errorf("tool selection failed: %w", err)
	}

	var combinedResponse string
	if len(toolSelections) == 0 {
		log.Printf("Orchestrator: No tools needed - processing as reflection")
		combinedResponse = fmt.Sprintf("Acknowledged: %s", input)
	} else {
		// Execute all selected tools and combine responses
		var allResponses []string
		for _, selection := range toolSelections {
			log.Printf("Orchestrator: Executing tool '%s' - Reason: %s", selection.ToolName, selection.Reason)
			
			tool := o.toolService.GetTool(selection.ToolName)
			if tool == nil {
				log.Printf("Warning: Tool '%s' not found, skipping", selection.ToolName)
				continue
			}
			
			toolResponse, err := tool.Execute(input)
			if err != nil {
				log.Printf("Warning: Tool '%s' execution failed: %v", selection.ToolName, err)
				continue
			}
			
			allResponses = append(allResponses, fmt.Sprintf("%s: %s", selection.ToolName, toolResponse))
		}

		if len(allResponses) == 0 {
			log.Printf("Orchestrator: No tools executed successfully - treating as reflection")
			combinedResponse = fmt.Sprintf("Acknowledged: %s", input)
		} else {
			// Combine all tool responses
			combinedResponse = fmt.Sprintf("Processed with %d tools: %s", len(allResponses), allResponses[0])
			if len(allResponses) > 1 {
				combinedResponse = fmt.Sprintf("Processed with %d tools: [%s]", len(allResponses), fmt.Sprintf("%v", allResponses))
			}
		}
	}

	// Let ProfileService analyze and learn from the input
	if err := o.profileService.ProcessInput(input); err != nil {
		log.Printf("Warning: Failed to process input for profile: %v", err)
	}

	log.Printf("Orchestrator: Generated response: %s", combinedResponse)
	return combinedResponse, nil
}