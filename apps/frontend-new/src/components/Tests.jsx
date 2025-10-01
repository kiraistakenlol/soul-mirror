// Test runner component for viewing and executing test scenarios

import { useState, useEffect } from 'react';
import api from '../services/api';
import TestScenario from './TestScenario';

export default function Tests() {
  const [view, setView] = useState('none'); // none, scenarios
  const [loading, setLoading] = useState(false);
  const [scenarios, setScenarios] = useState([]);
  const [scenarioStatus, setScenarioStatus] = useState({}); // Track status of each scenario
  const [scenarioResults, setScenarioResults] = useState({}); // Track results of each scenario

  // Auto-load scenarios on mount
  useEffect(() => {
    loadScenarios();
  }, []);

  async function loadScenarios() {
    setLoading(true);
    setView('scenarios');
    try {
      const data = await api.getTestScenarios();
      const loadedScenarios = data.scenarios || [];
      setScenarios(loadedScenarios);

      // Initialize status for all scenarios
      const initialStatus = {};
      loadedScenarios.forEach(scenario => {
        initialStatus[scenario.name] = 'idle';
      });
      setScenarioStatus(initialStatus);
    } catch (error) {
      setScenarios([]);
      console.error('Failed to load scenarios:', error);
    } finally {
      setLoading(false);
    }
  }

  async function runAllTests() {
    // Run all tests in parallel by calling runSingleScenario for each
    const testPromises = scenarios.map(scenario =>
      runSingleScenario(scenario.name)
    );

    // Wait for all tests to complete
    await Promise.allSettled(testPromises);
  }

  async function runSingleScenario(scenarioName) {
    // Mark as running
    setScenarioStatus(prev => ({ ...prev, [scenarioName]: 'running' }));

    try {
      const result = await api.runScenario(scenarioName);
      // Store result and mark as completed
      setScenarioResults(prev => ({ ...prev, [scenarioName]: result }));
      setScenarioStatus(prev => ({ ...prev, [scenarioName]: 'completed' }));
    } catch (error) {
      console.error('Failed to run scenario:', error);
      setScenarioStatus(prev => ({ ...prev, [scenarioName]: 'idle' }));
    }
  }

  return (
    <div className="bg-gray-900 rounded-lg p-6 h-[calc(100vh-140px)] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">🧪</span>
          <h2 className="text-lg font-semibold text-white">Prompt Tests</h2>
          {scenarios.length > 0 && (
            <span className="text-gray-400 text-sm">({scenarios.length} scenarios)</span>
          )}
        </div>

        <button
          onClick={runAllTests}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-4 py-2 rounded text-sm font-medium transition-colors"
        >
          {loading && view === 'results' ? 'Running...' : 'Run All Tests'}
        </button>
      </div>

      {/* Content area */}
      <div className="flex-1 overflow-y-auto space-y-3">
        {loading ? (
          <div className="text-blue-400 text-sm">Processing...</div>
        ) : view === 'scenarios' && scenarios.length > 0 ? (
          <>
            {scenarios.map((scenario, index) => (
              <TestScenario
                key={scenario.name}
                scenario={scenario}
                index={index}
                status={scenarioStatus[scenario.name] || 'idle'}
                result={scenarioResults[scenario.name]}
                onRun={runSingleScenario}
              />
            ))}
          </>
        ) : view === 'none' ? (
          <div className="text-gray-400 text-sm">
            Loading test scenarios...
          </div>
        ) : scenarios.length === 0 ? (
          <div className="text-gray-400 text-sm">No test scenarios available.</div>
        ) : null}
      </div>
    </div>
  );
}
