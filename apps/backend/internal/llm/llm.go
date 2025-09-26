package llm

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"

	"github.com/kirillsobolev/soul-mirror/backend/internal/config"
)

type ToolDescriptor struct {
	Name        string
	Description string
}

type ToolSelection struct {
	ToolName string
	Reason   string
}

type LLMService interface {
	SelectTools(userInput string, availableTools []ToolDescriptor) ([]ToolSelection, error)
	ProcessText(input string) (string, error)
}

type service struct {
	config *config.Config
	client *http.Client
}

func NewService(cfg *config.Config) LLMService {
	if cfg.HasAnthropicKey() {
		log.Println("✓ Anthropic client initialized")
	} else {
		log.Println("⚠️  No Anthropic API key - using fallback logic")
	}
	
	return &service{
		config: cfg,
		client: &http.Client{},
	}
}

func (s *service) SelectTools(userInput string, availableTools []ToolDescriptor) ([]ToolSelection, error) {
	log.Printf("🔍 LLM Tool Selection for: '%s'", userInput)

	if !s.config.HasAnthropicKey() {
		log.Printf("⚠️  No API key - using fallback selection")
		return s.fallbackToolSelection(userInput, availableTools)
	}

	log.Printf("📤 Asking Claude to select from %d available tools", len(availableTools))
	for _, tool := range availableTools {
		log.Printf("   • %s: %s", tool.Name, tool.Description)
	}

	prompt := s.buildToolSelectionPrompt(userInput, availableTools)
	response, err := s.callAnthropic(prompt)
	if err != nil {
		log.Printf("❌ Anthropic API error: %v", err)
		log.Printf("🔄 Falling back to simple selection")
		return s.fallbackToolSelection(userInput, availableTools)
	}

	selections, err := s.parseToolSelections(response)
	if err != nil {
		log.Printf("❌ Failed to parse Claude's response: %v", err)
		log.Printf("🔄 Falling back to simple selection")
		return s.fallbackToolSelection(userInput, availableTools)
	}

	if len(selections) == 0 {
		log.Printf("✅ Claude decided no tools are needed for this input")
	} else {
		log.Printf("✅ Claude selected %d tools:", len(selections))
		for i, sel := range selections {
			log.Printf("   %d. %s - %s", i+1, sel.ToolName, sel.Reason)
		}
	}

	return selections, nil
}

func (s *service) ProcessText(input string) (string, error) {
	log.Printf("📝 LLM Text Processing for: '%s'", input)
	
	if !s.config.HasAnthropicKey() {
		log.Printf("⚠️  No API key - using simple processing")
		response := "Processed (no LLM): " + input
		return response, nil
	}

	log.Printf("📤 Sending to Claude for processing...")
	prompt := fmt.Sprintf("Process and improve this user input for a personal intelligence system: %s", input)
	response, err := s.callAnthropic(prompt)
	if err != nil {
		log.Printf("❌ Anthropic API error: %v", err)
		return "Processed (API error): " + input, nil
	}

	log.Printf("✅ Claude response: '%s'", response)
	return response, nil
}

type anthropicRequest struct {
	Model     string    `json:"model"`
	MaxTokens int       `json:"max_tokens"`
	Messages  []message `json:"messages"`
}

type message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type anthropicResponse struct {
	Content []content `json:"content"`
}

type content struct {
	Text string `json:"text"`
}

func (s *service) callAnthropic(prompt string) (string, error) {
	// Log the prompt we're sending (truncated if very long)
	promptPreview := prompt
	if len(prompt) > 200 {
		promptPreview = prompt[:200] + "..."
	}
	log.Printf("🤖 → Claude: %s", promptPreview)

	reqBody := anthropicRequest{
		Model:     "claude-3-5-sonnet-20241022",
		MaxTokens: 1000,
		Messages: []message{
			{
				Role:    "user",
				Content: prompt,
			},
		},
	}

	reqJSON, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", "https://api.anthropic.com/v1/messages", bytes.NewBuffer(reqJSON))
	if err != nil {
		return "", err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-api-key", s.config.AnthropicAPIKey)
	req.Header.Set("anthropic-version", "2023-06-01")

	log.Printf("📡 Making API call to Anthropic...")
	resp, err := s.client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	log.Printf("📡 Response status: %d", resp.StatusCode)

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		log.Printf("❌ API Error Response: %s", string(body))
		return "", fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	var anthropicResp anthropicResponse
	if err := json.Unmarshal(body, &anthropicResp); err != nil {
		log.Printf("❌ Failed to parse response: %s", string(body))
		return "", err
	}

	if len(anthropicResp.Content) == 0 {
		return "", fmt.Errorf("empty response from Anthropic")
	}

	responseText := anthropicResp.Content[0].Text
	respPreview := responseText
	if len(responseText) > 300 {
		respPreview = responseText[:300] + "..."
	}
	log.Printf("🤖 ← Claude: %s", respPreview)

	return responseText, nil
}

func (s *service) buildToolSelectionPrompt(userInput string, tools []ToolDescriptor) string {
	toolsJSON, _ := json.MarshalIndent(tools, "", "  ")
	
	return fmt.Sprintf(`Given this user input: "%s"

Select the most appropriate tools from this list:
%s

Return a JSON array of tool selections with this format:
[
  {
    "tool_name": "tool_name",
    "reason": "explanation for why this tool was selected"
  }
]

IMPORTANT:
- You can select 0-3 tools based on what's most appropriate
- If no tools are suitable for this input, return an empty array: []
- Only select tools that would genuinely help process this specific input
- Don't force a selection if none of the tools are relevant`, userInput, string(toolsJSON))
}

func (s *service) parseToolSelections(response string) ([]ToolSelection, error) {
	// Extract JSON from response (it might have extra text)
	startIdx := strings.Index(response, "[")
	endIdx := strings.LastIndex(response, "]")
	
	if startIdx == -1 || endIdx == -1 {
		return nil, fmt.Errorf("no JSON array found in response")
	}
	
	jsonStr := response[startIdx : endIdx+1]
	
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

func (s *service) fallbackToolSelection(userInput string, availableTools []ToolDescriptor) ([]ToolSelection, error) {
	log.Printf("🔧 Using fallback tool selection")
	
	if len(availableTools) == 0 {
		log.Printf("❌ No tools available for fallback")
		return []ToolSelection{}, nil
	}
	
	// Simple fallback: select first tool
	selection := ToolSelection{
		ToolName: availableTools[0].Name,
		Reason:   "Fallback selection - first available tool",
	}
	
	log.Printf("✅ Fallback selected: %s - %s", selection.ToolName, selection.Reason)
	return []ToolSelection{selection}, nil
}