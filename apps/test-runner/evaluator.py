# LLM-based notes evaluator using OpenAI
import os
from openai import OpenAI
from dotenv import load_dotenv
import json as json_lib

load_dotenv()

class NotesEvaluator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-5-nano-2025-08-07"

    def evaluate(self, actual_notes: dict, expected: str, scenario_name: str) -> dict:
        """Evaluate if actual notes match expectations using LLM"""

        # Format notes data for evaluation
        notes_str = json_lib.dumps(actual_notes, indent=2)

        prompt = f"""You are evaluating a personal assistant's note-taking ability.

Scenario: {scenario_name}

Expected criteria:
{expected}

Actual notes data:
{notes_str if notes_str else "(no notes)"}

Do the actual notes meet the expected criteria? Respond with:
1. "passed": true/false
2. "reasoning": brief explanation (1-2 sentences)
3. "missing": list of missing elements (if any)
4. "unexpected": list of unexpected elements that should NOT be there (if any)

Format your response as JSON."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a test evaluator. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            return {
                "passed": False,
                "reasoning": f"Evaluation error: {str(e)}",
                "missing": [],
                "unexpected": []
            }