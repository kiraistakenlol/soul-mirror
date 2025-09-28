// llm provides integration with language models for intelligent tool selection and text processing.
package llm

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"strings"

	"github.com/kirillsobolev/soul-mirror/backend/internal/config"
)

type LLMService interface {
	SelectTools(userInput string, availableTools []ToolDescriptor) ([]ToolSelection, error)
	UpdateProfile(userInput string, currentProfile string, extractionTargets []ExtractionTarget) (*ProfileExtractionResponse, error)
}

type service struct {
	config   *config.Config
	provider Provider
}

func NewService(cfg *config.Config) LLMService {
	var provider Provider

	switch cfg.LLMProvider {
	case "openai":
		if cfg.HasOpenAIKey() {
			provider = NewOpenAIProvider(
				cfg.OpenAIAPIKey,
				"gpt-5-nano", // Default model - $0.05/1M input, $0.40/1M output
				"gpt-5-mini", // Advanced model - better performance, still cost-effective
			)
			log.Println("✓ OpenAI provider initialized")
		} else {
			log.Println("⚠️  No OpenAI API key - using fallback logic")
			return &fallbackService{}
		}
	case "anthropic":
		if cfg.HasAnthropicKey() {
			provider = NewAnthropicProvider(
				cfg.AnthropicAPIKey,
				"claude-3-5-haiku-20241022",  // Default model
				"claude-3-5-sonnet-20241022", // Advanced model for profile operations
			)
			log.Println("✓ Anthropic provider initialized")
		} else {
			log.Println("⚠️  No Anthropic API key - using fallback logic")
			return &fallbackService{}
		}
	default:
		log.Printf("⚠️  Unknown LLM provider '%s' - using fallback logic", cfg.LLMProvider)
		return &fallbackService{}
	}

	return &service{
		config:   cfg,
		provider: provider,
	}
}

func (s *service) SelectTools(userInput string, availableTools []ToolDescriptor) ([]ToolSelection, error) {
	log.Printf("🔍 LLM Tool Selection for: '%s'", userInput)

	log.Printf("📤 Asking %s to select from %d available tools", s.provider.GetName(), len(availableTools))
	for _, tool := range availableTools {
		log.Printf("   • %s: %s", tool.Name, tool.Description)
	}

	toolsJSON, _ := json.MarshalIndent(availableTools, "", "  ")
	userPrompt := fmt.Sprintf(ToolSelectionUserTemplate, userInput, string(toolsJSON))

	// Tool selection doesn't need advanced model
	response, err := s.provider.GenerateJSON(context.Background(), userPrompt, ToolSelectionSystemPrompt, false)
	if err != nil {
		log.Printf("❌ %s API error: %v", s.provider.GetName(), err)
		log.Printf("🔄 No tools selected due to API error")
		return []ToolSelection{}, nil
	}

	selections, err := s.parseToolSelections(response)
	if err != nil {
		log.Printf("❌ Failed to parse %s response: %v", s.provider.GetName(), err)
		log.Printf("🔄 No tools selected due to parsing error")
		return []ToolSelection{}, nil
	}

	if len(selections) == 0 {
		log.Printf("✅ %s decided no tools are needed for this input", s.provider.GetName())
	} else {
		log.Printf("✅ %s selected %d tools:", s.provider.GetName(), len(selections))
		for i, sel := range selections {
			log.Printf("   %d. %s - %s", i+1, sel.ToolName, sel.Reason)
		}
	}

	return selections, nil
}

func (s *service) UpdateProfile(userInput string, currentProfile string, extractionTargets []ExtractionTarget) (*ProfileExtractionResponse, error) {
	log.Printf("🧠 LLM Profile Extraction for: '%s'", userInput)

	// Profile operations use advanced model for better quality

	// Step 1: Extract structured data
	log.Printf("📤 Step 1: Extracting structured data from input...")
	extractionResults, err := s.extractStructuredData(userInput, currentProfile, extractionTargets)
	if err != nil {
		log.Printf("❌ %s extraction error: %v", s.provider.GetName(), err)
		return &ProfileExtractionResponse{
			UpdatedProfile:   currentProfile,
			ExtractedTargets: []ExtractionResult{},
		}, nil
	}

	// Check if any new information was found
	hasNewInfo := false
	for _, result := range extractionResults {
		if result.Found {
			hasNewInfo = true
			break
		}
	}

	// Step 2: Blend into natural description
	var updatedProfile string
	if hasNewInfo {
		log.Printf("📤 Step 2: Blending extracted data into profile...")
		updatedProfile, err = s.blendIntoProfile(currentProfile, extractionResults)
		if err != nil {
			log.Printf("❌ %s blending error: %v", s.provider.GetName(), err)
			return &ProfileExtractionResponse{
				UpdatedProfile:   currentProfile,
				ExtractedTargets: extractionResults,
			}, nil
		}
	} else {
		log.Printf("✅ No new information found, keeping profile unchanged")
		updatedProfile = currentProfile
	}

	log.Printf("✅ %s profile extraction completed", s.provider.GetName())
	return &ProfileExtractionResponse{
		UpdatedProfile:   updatedProfile,
		ExtractedTargets: extractionResults,
	}, nil
}

func (s *service) parseToolSelections(response string) ([]ToolSelection, error) {
	responseText := response
	startIdx := strings.Index(responseText, "[")
	endIdx := strings.LastIndex(responseText, "]")

	if startIdx == -1 || endIdx == -1 {
		return nil, fmt.Errorf("no JSON array found in response")
	}

	jsonStr := responseText[startIdx : endIdx+1]

	var rawSelections []struct {
		ToolName string `json:"tool_name"`
		Reason   string `json:"reason"`
	}

	if err := json.Unmarshal([]byte(jsonStr), &rawSelections); err != nil {
		return nil, err
	}

	selections := make([]ToolSelection, len(rawSelections))
	for i, raw := range rawSelections {
		selections[i] = ToolSelection{
			ToolName: raw.ToolName,
			Reason:   raw.Reason,
		}
	}

	return selections, nil
}

func (s *service) extractStructuredData(userInput string, currentProfile string, extractionTargets []ExtractionTarget) ([]ExtractionResult, error) {
	if currentProfile == "" {
		return s.extractFromEmptyProfile(userInput, extractionTargets)
	}
	return s.extractWithProfileComparison(userInput, currentProfile, extractionTargets)
}

func (s *service) extractFromEmptyProfile(userInput string, extractionTargets []ExtractionTarget) ([]ExtractionResult, error) {
	targetsJSON, _ := json.MarshalIndent(extractionTargets, "", "  ")
	userPrompt := fmt.Sprintf(ProfileExtractionEmptyTemplate, userInput, string(targetsJSON))

	// Use advanced model for profile extraction
	response, err := s.provider.GenerateJSON(context.Background(), userPrompt, ProfileExtractionSystemPrompt, true)
	if err != nil {
		return nil, err
	}

	return s.parseExtractionResults(response, extractionTargets)
}

func (s *service) extractWithProfileComparison(userInput string, currentProfile string, extractionTargets []ExtractionTarget) ([]ExtractionResult, error) {
	targetsJSON, _ := json.MarshalIndent(extractionTargets, "", "  ")
	userPrompt := fmt.Sprintf(ProfileExtractionComparisonTemplate, currentProfile, userInput, string(targetsJSON))

	// Use advanced model for profile extraction
	response, err := s.provider.GenerateJSON(context.Background(), userPrompt, ProfileExtractionSystemPrompt, true)
	if err != nil {
		return nil, err
	}

	return s.parseExtractionResults(response, extractionTargets)
}

func (s *service) blendIntoProfile(currentProfile string, extractionResults []ExtractionResult) (string, error) {
	// Build extracted data summary
	extractedData := ""
	for _, result := range extractionResults {
		if result.Found && result.Content != "" {
			extractedData += fmt.Sprintf("- %s: %s\n", result.TargetName, result.Content)
		}
	}

	if extractedData == "" {
		return currentProfile, nil
	}

	var prompt string
	if currentProfile == "" {
		// Create new profile
		prompt = fmt.Sprintf(ProfileBlendingNewTemplate, extractedData)
	} else {
		// Update existing profile
		prompt = fmt.Sprintf(ProfileBlendingUpdateTemplate, currentProfile, extractedData)
	}

	// Use advanced model for profile blending
	response, err := s.provider.GenerateText(context.Background(), prompt, ProfileBlendingSystemPrompt, true)
	if err != nil {
		return currentProfile, err
	}

	return strings.TrimSpace(response), nil
}

func (s *service) parseExtractionResults(response string, extractionTargets []ExtractionTarget) ([]ExtractionResult, error) {
	startIdx := strings.Index(response, "[")
	endIdx := strings.LastIndex(response, "]")

	if startIdx == -1 || endIdx == -1 {
		return nil, fmt.Errorf("no JSON array found in response")
	}

	jsonStr := response[startIdx : endIdx+1]

	var rawResults []struct {
		TargetName string `json:"target_name"`
		Content    string `json:"content"`
		Found      bool   `json:"found"`
	}

	if err := json.Unmarshal([]byte(jsonStr), &rawResults); err != nil {
		return nil, fmt.Errorf("failed to parse JSON: %v", err)
	}

	results := make([]ExtractionResult, len(extractionTargets))
	for i, target := range extractionTargets {
		results[i] = ExtractionResult{
			TargetName: target.Name,
			Content:    "",
			Found:      false,
		}

		// Find matching result from LLM response
		for _, raw := range rawResults {
			if raw.TargetName == target.Name {
				results[i].Content = raw.Content
				results[i].Found = raw.Found
				break
			}
		}
	}

	return results, nil
}
