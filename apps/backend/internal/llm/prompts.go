// prompts provides centralized prompt management for the LLM service.
package llm

// System prompts define the AI's role and behavior
const (
	// ToolSelectionSystemPrompt defines behavior for tool selection
	ToolSelectionSystemPrompt = `You are an intelligent assistant that selects appropriate tools based on user input.
You are conservative and only select tools when they are explicitly needed.
Most casual inputs don't require any tools - you should return an empty array in these cases.
Only select tools when the user explicitly asks for functionality that matches a tool's purpose.`

	// ProfileExtractionSystemPrompt defines behavior for profile information extraction
	ProfileExtractionSystemPrompt = `You are an expert at extracting and analyzing personal profile information.
You maintain strict factual accuracy and only extract information explicitly stated by the user.
You detect contradictions between old and new information, always preferring the most recent state.
You understand temporal markers (now, currently, recently, just) that indicate current state.
You never make assumptions or add interpretations beyond what is explicitly stated.`

	// ProfileBlendingSystemPrompt defines behavior for profile narrative creation
	ProfileBlendingSystemPrompt = `You are an expert at creating and maintaining personal profile narratives.
You write in first person, creating flowing, natural sentences.
You maintain factual accuracy and never embellish or interpret beyond provided information.
When updating profiles, you completely replace contradictory information with the most recent facts.
You keep profiles concise and focused on current state, not historical progression.`

	// TextProcessingSystemPrompt defines behavior for general text processing
	TextProcessingSystemPrompt = `You are a helpful assistant that processes and improves user input for a personal intelligence system.
You maintain the user's intent while improving clarity and structure.`

	// TextProcessingUserPrefix for text processing requests
	TextProcessingUserPrefix = "Process and improve this user input: "
)

// User prompt templates
const (
	// ToolSelectionUserTemplate for tool selection requests
	ToolSelectionUserTemplate = `Given this user input: "%s"

Available tools:
%s

Return a JSON array of tool selections with this format:
[
  {
    "tool_name": "tool_name",
    "reason": "explanation for why this tool was selected"
  }
]

Guidelines:
- Most inputs don't need any tools - return empty array [] in these cases
- Only select tools when the user explicitly asks for functionality that matches a tool
- Maximum 2 tools per input to keep responses focused
- Don't select tools just because they might be loosely related`

	// ProfileExtractionEmptyTemplate for extraction when no profile exists
	ProfileExtractionEmptyTemplate = `User Input: "%s"

Extraction Targets:
%s

Task: Extract factual information from the user input that matches any of the extraction targets.

Return a JSON array with this exact format:
[
  {
    "target_name": "target_name",
    "content": "extracted information or empty string",
    "found": true/false
  }
]

Rules:
- Only extract information explicitly stated by the user
- Only include targets where information was actually found
- Be precise and factual`

	// ProfileExtractionComparisonTemplate for extraction with existing profile
	ProfileExtractionComparisonTemplate = `Current Profile:
"""
%s
"""

User Input: "%s"

Extraction Targets:
%s

Task: Extract information from the user input that updates the profile.

Critical Rules:
- If user states a CURRENT fact that contradicts the profile, extract it
- Present tense statements override past information
- "I live in X" overrides "I live in Y" 
- "I moved to X" means no longer in previous location
- Recent temporal markers (now, currently, just, recently) indicate current state

Return a JSON array with this exact format:
[
  {
    "target_name": "target_name",
    "content": "the CURRENT state/fact that replaces old information",
    "found": true
  }
]

Only include:
- NEW information not in profile
- UPDATES that contradict/replace existing facts
- Focus on CURRENT STATE, not historical information`

	// ProfileBlendingNewTemplate for creating new profile
	ProfileBlendingNewTemplate = `Extracted Information:
%s

Task: Create a simple first-person narrative profile from ONLY the extracted information above.

CRITICAL REQUIREMENTS:
- Use ONLY the facts provided above - DO NOT add interpretations, elaborations, or assumptions
- Write as a flowing narrative using connected sentences
- Keep it factual and concise
- DO NOT add emotional content, explanations, or background stories
- DO NOT make assumptions about personality, feelings, or experiences
- Use the exact information provided without embellishment

Example: If extracted info is "name: John, born: Russia, job: developer" → "I'm John. I was born in Russia and work as a developer."

IMPORTANT: Write as connected sentences, not separate bullet points or lines.

Return only the factual profile text, no additional formatting.`

	// ProfileBlendingUpdateTemplate for updating existing profile
	ProfileBlendingUpdateTemplate = `Current Profile:
"""
%s
"""

New/Updated Information:
%s

Task: Update the profile with the new information, REPLACING any contradictory facts.

CRITICAL CONTRADICTION HANDLING:
- If new info contradicts old info, COMPLETELY REPLACE the old with new
- Remove ALL outdated information that conflicts with updates
- Keep only the MOST RECENT state of any fact
- Do NOT keep both old and new versions of the same fact

Examples of replacements:
- Old: "living in Buenos Aires" + New: "living in Moscow" → Keep ONLY "living in Moscow"
- Old: "planning to move to X" + New: "moved to Y" → Keep ONLY "living in Y" (remove planning)
- Old: "have a dog Max" + New: "dog died, got new dog Jack" → Keep ONLY "have a dog Jack"

REQUIREMENTS:
- Maintain factual, concise narrative style
- Use connected sentences, not bullet points
- ONLY include current facts, not historical progression
- Remove any contradicted or outdated information
- Keep non-contradicted information unchanged

Return only the updated profile text with current facts, no additional formatting.`
)