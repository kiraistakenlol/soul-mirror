# Test scenario execution orchestrator
import requests
import json
from datetime import datetime
from typing import List, Dict
from evaluator import NotesEvaluator

BACKEND_URL = "http://localhost:8080"

class TestRunner:
    def __init__(self):
        self.evaluator = NotesEvaluator()

    def load_scenarios(self) -> List[Dict]:
        """Load test scenarios from JSON file"""
        with open('test-scenarios.json', 'r') as f:
            return json.load(f)

    def run_scenario(self, scenario: Dict) -> Dict:
        """Execute a single test scenario with unique user_id (no reset needed)"""
        name = scenario["name"]
        inputs = scenario["inputs"]
        expectations = scenario["notesExpectations"]

        # Generate unique user_id: test-{scenarioName}-{datetime}
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        user_id = f"test-{name.replace(' ', '_')}-{timestamp}"

        print(f"\n{'='*60}")
        print(f"Running scenario: {name}")
        print(f"User ID: {user_id}")
        print(f"{'='*60}")

        # Execute input sequence
        responses = []
        for idx, user_input in enumerate(inputs, 1):
            print(f"\nInput {idx}/{len(inputs)}: {user_input}")
            try:
                resp = requests.get(
                    f"{BACKEND_URL}/api/process",
                    params={"input": user_input, "user_id": user_id},
                    timeout=30
                )
                if resp.status_code == 200:
                    responses.append(resp.json())
                    print(f"✓ Response received")
                else:
                    print(f"✗ Process failed: {resp.status_code}")
                    return {
                        "scenario": name,
                        "passed": False,
                        "error": f"Process failed: {resp.status_code}"
                    }
            except Exception as e:
                print(f"✗ Request failed: {str(e)}")
                return {
                    "scenario": name,
                    "passed": False,
                    "error": f"Request failed: {str(e)}"
                }

        # Fetch final notes
        print(f"\nFetching notes for user_id: {user_id}")
        try:
            notes_resp = requests.get(
                f"{BACKEND_URL}/api/notes",
                params={"user_id": user_id}
            )
            notes_data = notes_resp.json()
            print(f"Notes received: {notes_data.get('notes_count', 0)} notes in {notes_data.get('groups_count', 0)} groups")
        except Exception as e:
            print(f"✗ Failed to fetch notes: {str(e)}")
            return {
                "scenario": name,
                "passed": False,
                "error": f"Failed to fetch notes: {str(e)}"
            }

        # Evaluate with LLM
        print(f"\nEvaluating notes...")
        evaluation = self.evaluator.evaluate(notes_data, expectations, name)
        print(f"Result: {'✓ PASSED' if evaluation.get('passed') else '✗ FAILED'}")

        return {
            "scenario": name,
            "passed": evaluation.get("passed", False),
            "reasoning": evaluation.get("reasoning", ""),
            "missing": evaluation.get("missing", []),
            "unexpected": evaluation.get("unexpected", []),
            "actual_notes": notes_data,
            "expectations": expectations
        }

    def run_all(self) -> Dict:
        """Execute all test scenarios"""
        scenarios = self.load_scenarios()
        results = []

        for scenario in scenarios:
            result = self.run_scenario(scenario)
            results.append(result)

        passed_count = sum(1 for r in results if r.get("passed", False))
        total_count = len(results)

        return {
            "summary": {
                "total": total_count,
                "passed": passed_count,
                "failed": total_count - passed_count
            },
            "results": results
        }