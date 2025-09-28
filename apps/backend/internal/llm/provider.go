// provider defines the interface for LLM providers.
package llm

import "context"

// Provider interface for different LLM implementations
type Provider interface {
	// GenerateText generates plain text response
	// advanced parameter uses more capable model when true
	GenerateText(ctx context.Context, userPrompt, systemPrompt string, advanced bool) (string, error)

	// GenerateJSON generates JSON-formatted response
	// advanced parameter uses more capable model when true
	GenerateJSON(ctx context.Context, userPrompt, systemPrompt string, advanced bool) (string, error)

	// GetName returns the provider name for logging
	GetName() string
}
