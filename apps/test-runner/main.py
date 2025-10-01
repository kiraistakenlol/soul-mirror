# FastAPI server for test runner
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from runner import TestRunner

app = FastAPI(title="Soul Mirror Test Runner", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize test runner
runner = TestRunner()

@app.get("/api/scenarios")
def get_scenarios():
    """Get all test scenarios"""
    try:
        scenarios = runner.load_scenarios()
        return {
            "scenarios": scenarios,
            "count": len(scenarios)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/run-all")
def run_all_tests():
    """Execute all test scenarios"""
    try:
        results = runner.run_all()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/run-scenario")
def run_single_scenario(scenario_name: str):
    """Execute a single test scenario by name"""
    try:
        scenarios = runner.load_scenarios()
        scenario = next((s for s in scenarios if s["name"] == scenario_name), None)

        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario '{scenario_name}' not found")

        result = runner.run_scenario(scenario)

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
def get_status():
    """Health check"""
    return {
        "status": "healthy",
        "service": "test-runner",
        "backend_url": "http://localhost:8080"
    }

@app.get("/")
def root():
    return {"message": "Soul Mirror Test Runner API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8081,
        reload=True
    )