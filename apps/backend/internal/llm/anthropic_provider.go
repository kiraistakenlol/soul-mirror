// anthropic_provider implements the Provider interface for Claude models.
package llm

import (
	"context"
	"fmt"
	"log"
	"strings"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/anthropics/anthropic-sdk-go/option"
)

type AnthropicProvider struct {
	client        anthropic.Client
	model         string
	advancedModel string
}

func NewAnthropicProvider(apiKey, model, advancedModel string) Provider {
	client := anthropic.NewClient(option.WithAPIKey(apiKey))
	return &AnthropicProvider{
		client:        client,
		model:         model,
		advancedModel: advancedModel,
	}
}

func (p *AnthropicProvider) GetName() string {
	return "anthropic"
}

func (p *AnthropicProvider) GenerateText(ctx context.Context, userPrompt, systemPrompt string, advanced bool) (string, error) {
	return p.callAnthropic(ctx, userPrompt, systemPrompt, advanced)
}

func (p *AnthropicProvider) GenerateJSON(ctx context.Context, userPrompt, systemPrompt string, advanced bool) (string, error) {
	response, err := p.callAnthropic(ctx, userPrompt, systemPrompt, advanced)
	if err != nil {
		return "", err
	}

	// Clean JSON markers if present
	response = strings.TrimSpace(response)
	if strings.HasPrefix(response, "```json") {
		response = strings.TrimPrefix(response, "```json")
		response = strings.TrimSuffix(response, "```")
		response = strings.TrimSpace(response)
	}

	return response, nil
}

func (p *AnthropicProvider) callAnthropic(ctx context.Context, userPrompt, systemPrompt string, advanced bool) (string, error) {
	model := p.model
	if advanced && p.advancedModel != "" {
		model = p.advancedModel
		log.Printf("🤖 → Claude (Advanced - %s)", model)
	} else {
		log.Printf("🤖 → Claude (%s)", model)
	}

	// Log prompt preview
	promptPreview := userPrompt
	if len(userPrompt) > 200 {
		promptPreview = userPrompt[:200] + "..."
	}
	log.Printf("User prompt: %s", promptPreview)

	// Build request parameters
	params := anthropic.MessageNewParams{
		Model:     anthropic.Model(model),
		MaxTokens: int64(2000),
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock(userPrompt)),
		},
	}

	// Add system prompt if provided
	if systemPrompt != "" {
		params.System = []anthropic.TextBlockParam{
			{
				Text: systemPrompt,
			},
		}
	}

	log.Printf("📡 Making API call to Anthropic...")

	// Make API call
	message, err := p.client.Messages.New(ctx, params)
	if err != nil {
		log.Printf("❌ Anthropic API error: %v", err)
		return "", fmt.Errorf("Anthropic API error: %w", err)
	}

	log.Printf("📡 Response received from Anthropic")

	// Extract response text
	if len(message.Content) == 0 {
		return "", fmt.Errorf("empty response from Anthropic")
	}

	// Get first text block from response
	var responseText string
	for _, content := range message.Content {
		// Use AsAny to switch on the variant
		switch v := content.AsAny().(type) {
		case anthropic.TextBlock:
			responseText = v.Text
			break
		}
	}

	if responseText == "" {
		return "", fmt.Errorf("no text content in Anthropic response")
	}

	respPreview := responseText
	if len(responseText) > 300 {
		respPreview = responseText[:300] + "..."
	}
	log.Printf("🤖 ← Claude: %s", respPreview)

	return responseText, nil
}
