package orchestrator

import (
	"fmt"
	"log"
	"time"

	"github.com/kirillsobolev/soul-mirror/backend/internal/types"
	"github.com/kirillsobolev/soul-mirror/backend/internal/llm"
	"github.com/kirillsobolev/soul-mirror/backend/internal/profile"
	"github.com/kirillsobolev/soul-mirror/backend/internal/tools"
)

type Orchestrator interface {
	ProcessInput(input string) (string, error)
	ProcessInputDetailed(input string) (*types.ProcessResponse, error)
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
	detailed, err := o.ProcessInputDetailed(input)
	if err != nil {
		return "", err
	}
	return detailed.Result.FinalResponse, nil
}

func (o *orchestrator) ProcessInputDetailed(input string) (*types.ProcessResponse, error) {
	startTime := time.Now()
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
	llmStart := time.Now()
	toolSelections, err := o.llmService.SelectTools(input, toolDescriptors)
	llmDuration := time.Since(llmStart)
	if err != nil {
		return nil, fmt.Errorf("tool selection failed: %w", err)
	}

	// Convert llm.ToolSelection to types.ToolSelection
	apiToolSelections := make([]types.ToolSelection, len(toolSelections))
	for i, sel := range toolSelections {
		apiToolSelections[i] = types.ToolSelection{
			ToolName: sel.ToolName,
			Reason:   sel.Reason,
		}
	}

	var combinedResponse string
	var toolExecutions []types.ToolExecution

	if len(toolSelections) == 0 {
		log.Printf("Orchestrator: No tools needed - processing as reflection")
		combinedResponse = fmt.Sprintf("Acknowledged: %s", input)
	} else {
		// Execute all selected tools and combine responses
		var allResponses []string
		for _, selection := range toolSelections {
			log.Printf("Orchestrator: Executing tool '%s' - Reason: %s", selection.ToolName, selection.Reason)
			
			toolStart := time.Now()
			tool := o.toolService.GetTool(selection.ToolName)
			if tool == nil {
				log.Printf("Warning: Tool '%s' not found, skipping", selection.ToolName)
				toolExecutions = append(toolExecutions, types.ToolExecution{
					ToolName:      selection.ToolName,
					Input:         input,
					Output:        "",
					ExecutionTime: time.Since(toolStart).String(),
					Status:        "skipped",
					Error:         "Tool not found",
				})
				continue
			}
			
			toolResponse, err := tool.Execute(input)
			toolDuration := time.Since(toolStart)
			
			if err != nil {
				log.Printf("Warning: Tool '%s' execution failed: %v", selection.ToolName, err)
				toolExecutions = append(toolExecutions, types.ToolExecution{
					ToolName:      selection.ToolName,
					Input:         input,
					Output:        "",
					ExecutionTime: toolDuration.String(),
					Status:        "error",
					Error:         err.Error(),
				})
				continue
			}
			
			toolExecutions = append(toolExecutions, types.ToolExecution{
				ToolName:      selection.ToolName,
				Input:         input,
				Output:        toolResponse,
				ExecutionTime: toolDuration.String(),
				Status:        "success",
			})
			
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
	profileStart := time.Now()
	profileLengthBefore := len(o.getProfileSafely())
	err = o.profileService.ProcessInput(input)
	profileDuration := time.Since(profileStart)
	profileSuccess := err == nil
	profileLengthAfter := len(o.getProfileSafely())
	
	if err != nil {
		log.Printf("Warning: Failed to process input for profile: %v", err)
	}

	totalDuration := time.Since(startTime)
	log.Printf("Orchestrator: Generated response: %s", combinedResponse)

	response := &types.ProcessResponse{
		Input: input,
		Result: types.ProcessResult{
			FinalResponse: combinedResponse,
			ProcessingDetails: types.ProcessingDetails{
				LLMAnalysis: types.LLMAnalysisResult{
					ToolsConsidered: len(toolDescriptors),
					ToolsSelected:   apiToolSelections,
					ProcessingTime:  llmDuration.String(),
					UsedFallback:    false, // TODO: detect actual fallback usage
				},
				ToolExecutions: toolExecutions,
				ProfileUpdate: types.ProfileUpdate{
					ChangesMade:         "Added user input to profile",
					ProfileLengthBefore: profileLengthBefore,
					ProfileLengthAfter:  profileLengthAfter,
					ProcessingTime:      profileDuration.String(),
					Success:             profileSuccess,
				},
			},
			Metadata: types.ProcessMetadata{
				TotalProcessingTime: totalDuration.String(),
				Timestamp:           time.Now(),
				ToolsExecuted:       len(toolExecutions),
				LLMCallsMade:        1,
				Environment:         "development", // TODO: get from config
			},
		},
	}

	return response, nil
}

func (o *orchestrator) getProfileSafely() string {
	profile, err := o.profileService.Get()
	if err != nil {
		return ""
	}
	return profile
}