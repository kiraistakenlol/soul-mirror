// llm provides integration with language models for intelligent tool selection and text processing.
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

type LLMService interface {
	SelectTools(userInput string, availableTools []ToolDescriptor) ([]ToolSelection, error)
	ProcessText(input string) (string, error)
}

type service struct {
	config *config.Config
	client *http.Client
}

func NewService(cfg *config.Config) LLMService {
	switch cfg.LLMProvider {
	case "openai":
		if cfg.HasOpenAIKey() {
			log.Println("✓ OpenAI client initialized")
		} else {
			log.Println("⚠️  No OpenAI API key - using fallback logic")
		}
	case "anthropic":
		if cfg.HasAnthropicKey() {
			log.Println("✓ Anthropic client initialized")
		} else {
			log.Println("⚠️  No Anthropic API key - using fallback logic")
		}
	default:
		log.Printf("⚠️  Unknown LLM provider '%s' - using fallback logic", cfg.LLMProvider)
	}

	return &service{
		config: cfg,
		client: &http.Client{},
	}
}

func (s *service) SelectTools(userInput string, availableTools []ToolDescriptor) ([]ToolSelection, error) {
	log.Printf("🔍 LLM Tool Selection for: '%s'", userInput)

	if !s.config.HasLLMKey() {
		log.Printf("⚠️  No API key - no tools selected")
		return []ToolSelection{}, nil
	}

	log.Printf("📤 Asking %s to select from %d available tools", s.config.LLMProvider, len(availableTools))
	for _, tool := range availableTools {
		log.Printf("   • %s: %s", tool.Name, tool.Description)
	}

	prompt := s.buildToolSelectionPrompt(userInput, availableTools)
	response, err := s.callLLM(prompt)
	if err != nil {
		log.Printf("❌ %s API error: %v", s.config.LLMProvider, err)
		log.Printf("🔄 No tools selected due to API error")
		return []ToolSelection{}, nil
	}

	selections, err := s.parseToolSelections(response)
	if err != nil {
		log.Printf("❌ Failed to parse %s response: %v", s.config.LLMProvider, err)
		log.Printf("🔄 No tools selected due to parsing error")
		return []ToolSelection{}, nil
	}

	if len(selections) == 0 {
		log.Printf("✅ %s decided no tools are needed for this input", s.config.LLMProvider)
	} else {
		log.Printf("✅ %s selected %d tools:", s.config.LLMProvider, len(selections))
		for i, sel := range selections {
			log.Printf("   %d. %s - %s", i+1, sel.ToolName, sel.Reason)
		}
	}

	return selections, nil
}

func (s *service) ProcessText(input string) (string, error) {
	log.Printf("📝 LLM Text Processing for: '%s'", input)

	if !s.config.HasLLMKey() {
		log.Printf("⚠️  No API key - using simple processing")
		response := "Processed (no LLM): " + input
		return response, nil
	}

	log.Printf("📤 Sending to %s for processing...", s.config.LLMProvider)
	prompt := fmt.Sprintf("Process and improve this user input for a personal intelligence system: %s", input)
	response, err := s.callLLM(prompt)
	if err != nil {
		log.Printf("❌ %s API error: %v", s.config.LLMProvider, err)
		return "Processed (API error): " + input, nil
	}

	log.Printf("✅ %s response: '%s'", s.config.LLMProvider, response)
	return response, nil
}

type anthropicRequest struct {
	Model     string    `json:"model"`
	MaxTokens int       `json:"max_tokens"`
	Messages  []message `json:"messages"`
}

type openaiRequest struct {
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

type openaiResponse struct {
	Choices []choice `json:"choices"`
}

type choice struct {
	Message message `json:"message"`
}

type content struct {
	Text string `json:"text"`
}

func (s *service) callLLM(prompt string) (string, error) {
	switch s.config.LLMProvider {
	case "openai":
		return s.callOpenAI(prompt)
	case "anthropic":
		return s.callAnthropic(prompt)
	default:
		return "", fmt.Errorf("unsupported LLM provider: %s", s.config.LLMProvider)
	}
}

func (s *service) callAnthropic(prompt string) (string, error) {
	promptPreview := prompt
	if len(prompt) > 200 {
		promptPreview = prompt[:200] + "..."
	}
	log.Printf("🤖 → Claude: %s", promptPreview)

	reqBody := anthropicRequest{
		Model:     "claude-3-5-haiku-20241022",
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

Available tools:
%s

Return a JSON array of tool selections with this format:
[
  {
    "tool_name": "tool_name",
    "reason": "explanation for why this tool was selected"
  }
]

IMPORTANT GUIDELINES:
- Most inputs don't need any tools - return empty array [] in these cases
- Only select tools when the user explicitly asks for functionality that matches a tool
- Don't select tools just because they might be loosely related to the input
- Expressions of feelings, thoughts, or general statements rarely need tools
- When in doubt, prefer no tools over unnecessary tools
- Maximum 2 tools per input to keep responses focused`, userInput, string(toolsJSON))
}

func (s *service) parseToolSelections(response string) ([]ToolSelection, error) {
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

func (s *service) callOpenAI(prompt string) (string, error) {
	promptPreview := prompt
	if len(prompt) > 200 {
		promptPreview = prompt[:200] + "..."
	}
	log.Printf("🤖 → OpenAI: %s", promptPreview)

	reqBody := openaiRequest{
		Model:     "gpt-4.1-nano",
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

	req, err := http.NewRequest("POST", "https://api.openai.com/v1/chat/completions", bytes.NewBuffer(reqJSON))
	if err != nil {
		return "", err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+s.config.OpenAIAPIKey)

	log.Printf("📡 Making API call to OpenAI...")
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

	var openaiResp openaiResponse
	if err := json.Unmarshal(body, &openaiResp); err != nil {
		log.Printf("❌ Failed to parse response: %s", string(body))
		return "", err
	}

	if len(openaiResp.Choices) == 0 {
		return "", fmt.Errorf("empty response from OpenAI")
	}

	responseText := openaiResp.Choices[0].Message.Content
	respPreview := responseText
	if len(responseText) > 300 {
		respPreview = responseText[:300] + "..."
	}
	log.Printf("🤖 ← OpenAI: %s", respPreview)

	return responseText, nil
}
