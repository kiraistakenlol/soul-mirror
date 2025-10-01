# LLM-based profile evaluator using OpenAI
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ProfileEvaluator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-5-nano-2025-08-07"

    def evaluate(self, actual_profile: str, expected: str, scenario_name: str) -> dict:
        """Evaluate if actual profile matches expectations using LLM"""

        prompt = f"""You are evaluating a personal assistant's profile extraction ability.

Scenario: {scenario_name}

Expected criteria:
{expected}

Actual profile:
{actual_profile if actual_profile else "(empty profile)"}

Does the actual profile meet the expected criteria? Respond with:
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