// orchestrator coordinates the workflow between LLM, tool, and profile services to process user input.
package orchestrator

import (
	"fmt"
	"log"
	"time"

	"github.com/kirillsobolev/soul-mirror/backend/internal/llm"
	"github.com/kirillsobolev/soul-mirror/backend/internal/profile"
	"github.com/kirillsobolev/soul-mirror/backend/internal/tools"
)

type Orchestrator interface {
	ProcessInput(input string) (*ProcessResponse, error)
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

func (o *orchestrator) ProcessInput(input string) (*ProcessResponse, error) {
	startTime := time.Now()
	log.Printf("Orchestrator: Processing input: %s", input)

	profile := o.updateAndGetProfile(input)
	tools := o.getAvailableTools()
	selectedTools, err := o.selectTools(input, tools)
	if err != nil {
		return nil, fmt.Errorf("tool selection failed: %w", err)
	}

	toolExecutions := o.executeTools(input, selectedTools, profile)
	return o.buildResponse(input, selectedTools, toolExecutions, startTime), nil
}

func (o *orchestrator) updateAndGetProfile(input string) string {
	err := o.profileService.ProcessInput(input)
	if err != nil {
		log.Printf("Warning: Failed to process input for profile: %v", err)
	}
	return o.getProfileSafely()
}

func (o *orchestrator) getAvailableTools() []llm.ToolDescriptor {
	toolsList := o.toolService.ListTools()
	toolDescriptors := make([]llm.ToolDescriptor, len(toolsList))
	for i, tool := range toolsList {
		toolDescriptors[i] = llm.ToolDescriptor{
			Name:        tool.Name(),
			Description: tool.Description(),
		}
	}
	return toolDescriptors
}

func (o *orchestrator) selectTools(input string, tools []llm.ToolDescriptor) ([]llm.ToolSelection, error) {
	toolSelections, err := o.llmService.SelectTools(input, tools)
	return toolSelections, err
}

func (o *orchestrator) executeTools(input string, toolSelections []llm.ToolSelection, profile string) []ToolExecution {
	if len(toolSelections) == 0 {
		log.Printf("Orchestrator: No tools needed - processing as reflection")
		return []ToolExecution{}
	}

	var toolExecutions []ToolExecution
	context := tools.Context{Profile: profile}

	for _, selection := range toolSelections {
		execution := o.executeSingleTool(input, selection, context)
		toolExecutions = append(toolExecutions, execution)
	}

	return toolExecutions
}

func (o *orchestrator) executeSingleTool(input string, selection llm.ToolSelection, context tools.Context) ToolExecution {
	log.Printf("Orchestrator: Executing tool '%s' - Reason: %s", selection.ToolName, selection.Reason)
	toolStart := time.Now()
	
	tool := o.toolService.GetTool(selection.ToolName)
	if tool == nil {
		log.Printf("Warning: Tool '%s' not found, skipping", selection.ToolName)
		return ToolExecution{
			ToolName:      selection.ToolName,
			Input:         input,
			ExecutionTime: time.Since(toolStart).String(),
			Status:        "skipped",
			Error:         "Tool not found",
		}
	}
	
	toolResponse, err := tool.Execute(input, context)
	status := "success"
	errorMsg := ""
	
	if err != nil {
		log.Printf("Warning: Tool '%s' execution failed: %v", selection.ToolName, err)
		status = "error"
		errorMsg = err.Error()
	}
	
	return ToolExecution{
		ToolName:      selection.ToolName,
		Input:         input,
		Output:        toolResponse,
		ExecutionTime: time.Since(toolStart).String(),
		Status:        status,
		Error:         errorMsg,
	}
}

func (o *orchestrator) buildFinalResponse(input string, toolSelections []llm.ToolSelection, toolExecutions []ToolExecution) string {
	if len(toolSelections) == 0 {
		return fmt.Sprintf("Acknowledged: %s", input)
	}

	var allResponses []string
	for _, execution := range toolExecutions {
		if execution.Status == "success" {
			allResponses = append(allResponses, fmt.Sprintf("%s: %s", execution.ToolName, execution.Output))
		}
	}

	if len(allResponses) == 0 {
		log.Printf("Orchestrator: No tools executed successfully - treating as reflection")
		return fmt.Sprintf("Acknowledged: %s", input)
	}

	if len(allResponses) == 1 {
		return fmt.Sprintf("Processed with %d tools: %s", len(allResponses), allResponses[0])
	}
	return fmt.Sprintf("Processed with %d tools: [%s]", len(allResponses), fmt.Sprintf("%v", allResponses))
}

func (o *orchestrator) buildResponse(input string, selectedTools []llm.ToolSelection, toolExecutions []ToolExecution, startTime time.Time) *ProcessResponse {
	finalResponse := o.buildFinalResponse(input, selectedTools, toolExecutions)
	log.Printf("Orchestrator: Generated response: %s", finalResponse)

	return &ProcessResponse{
		Input: input,
		Result: ProcessResult{
			FinalResponse: finalResponse,
			ProcessingDetails: ProcessingDetails{
				LLMAnalysis: LLMAnalysisResult{
					ToolsConsidered: len(o.getAvailableTools()),
					ToolsSelected:   selectedTools,
					ProcessingTime:  "0ms", // Simplified for cleaner interface
					UsedFallback:    false,
				},
				ToolExecutions: toolExecutions,
				ProfileUpdate: ProfileUpdate{
					ChangesMade: "Added user input to profile",
					ProcessingTime: "0ms", // Simplified for cleaner interface
					Success: true,
				},
			},
			Metadata: ProcessMetadata{
				TotalProcessingTime: time.Since(startTime).String(),
				Timestamp:           time.Now(),
				ToolsExecuted:       len(toolExecutions),
				LLMCallsMade:        1,
				Environment:         "development",
			},
		},
	}
}

func (o *orchestrator) getProfileSafely() string {
	profile, err := o.profileService.Get()
	if err != nil {
		return ""
	}
	return profile
}