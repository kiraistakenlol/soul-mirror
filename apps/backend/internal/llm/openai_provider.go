// openai_provider implements the Provider interface for OpenAI models.
package llm

import (
	"context"
	"fmt"
	"log"
	"strings"

	"github.com/openai/openai-go"
	"github.com/openai/openai-go/option"
)

type OpenAIProvider struct {
	client        openai.Client
	model         string
	advancedModel string
}

func NewOpenAIProvider(apiKey, model, advancedModel string) Provider {
	client := openai.NewClient(option.WithAPIKey(apiKey))
	return &OpenAIProvider{
		client:        client,
		model:         model,
		advancedModel: advancedModel,
	}
}

func (p *OpenAIProvider) GetName() string {
	return "openai"
}

func (p *OpenAIProvider) GenerateText(ctx context.Context, userPrompt, systemPrompt string, advanced bool) (string, error) {
	return p.callOpenAI(ctx, userPrompt, systemPrompt, advanced)
}

func (p *OpenAIProvider) GenerateJSON(ctx context.Context, userPrompt, systemPrompt string, advanced bool) (string, error) {
	response, err := p.callOpenAI(ctx, userPrompt, systemPrompt, advanced)
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

func (p *OpenAIProvider) callOpenAI(ctx context.Context, userPrompt, systemPrompt string, advanced bool) (string, error) {
	model := p.model
	if advanced && p.advancedModel != "" {
		model = p.advancedModel
		log.Printf("🤖 → OpenAI (Advanced - %s)", model)
	} else {
		log.Printf("🤖 → OpenAI (%s)", model)
	}
	
	// Log prompt preview
	promptPreview := userPrompt
	if len(userPrompt) > 200 {
		promptPreview = userPrompt[:200] + "..."
	}
	log.Printf("User prompt: %s", promptPreview)
	
	// Build messages array
	var messages []openai.ChatCompletionMessageParamUnion
	
	// OpenAI includes system prompt as a message
	if systemPrompt != "" {
		messages = append(messages, openai.SystemMessage(systemPrompt))
	}
	messages = append(messages, openai.UserMessage(userPrompt))
	
	log.Printf("📡 Making API call to OpenAI...")
	
	var modelParam openai.ChatModel
	switch model {
	case "gpt-4o":
		modelParam = openai.ChatModelGPT4o
	case "gpt-4o-mini":
		modelParam = openai.ChatModelGPT4oMini
	default:
		// Default to gpt-4o-mini if model string doesn't match
		modelParam = openai.ChatModelGPT4oMini
	}
	
	chatCompletion, err := p.client.Chat.Completions.New(ctx, openai.ChatCompletionNewParams{
		Messages: messages,
		Model:    modelParam,
	})
	
	if err != nil {
		log.Printf("❌ OpenAI API error: %v", err)
		return "", fmt.Errorf("OpenAI API error: %w", err)
	}
	
	log.Printf("📡 Response received from OpenAI")
	
	if len(chatCompletion.Choices) == 0 {
		return "", fmt.Errorf("empty response from OpenAI")
	}
	
	responseText := chatCompletion.Choices[0].Message.Content
	respPreview := responseText
	if len(responseText) > 300 {
		respPreview = responseText[:300] + "..."
	}
	log.Printf("🤖 ← OpenAI: %s", respPreview)
	
	return responseText, nil
}