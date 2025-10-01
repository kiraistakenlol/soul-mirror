// Single test scenario card

import { useState } from 'react';

export default function TestScenario({ scenario, index, status, result, onRun }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const statusConfig = {
    idle: {
      bg: 'bg-slate-700',
      text: 'text-slate-300',
      border: 'border-slate-600',
      label: 'Ready',
      icon: '○'
    },
    running: {
      bg: 'bg-blue-600',
      text: 'text-white',
      border: 'border-blue-500',
      label: 'Running',
      icon: '◐'
    },
    completed: {
      bg: result?.passed ? 'bg-emerald-600' : 'bg-red-600',
      text: 'text-white',
      border: result?.passed ? 'border-emerald-500' : 'border-red-500',
      label: result?.passed ? 'Passed' : 'Failed',
      icon: result?.passed ? '✓' : '✗'
    },
  };
  const config = statusConfig[status];

  return (
    <div className={`bg-gradient-to-br from-gray-800 to-gray-850 rounded-xl border-2 ${config.border} hover:border-gray-600 transition-all duration-200 shadow-lg`}>
      {/* Header - always visible */}
      <div className="p-4 flex items-center justify-between gap-4">
        {/* Left: Expand toggle + Number + Title */}
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {/* Expand/Collapse button */}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex-shrink-0 text-gray-400 hover:text-white transition-colors"
          >
            <svg
              className={`w-5 h-5 transform transition-transform ${isExpanded ? 'rotate-90' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>

          {/* Number badge */}
          <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center text-white font-bold text-sm shadow-md">
            {index + 1}
          </div>

          {/* Title */}
          <h3 className="text-sm font-semibold text-white truncate">{scenario.name}</h3>
        </div>

        {/* Right: Status + Run button */}
        <div className="flex items-center gap-3 flex-shrink-0">
          {/* Status badge */}
          <div className={`${config.bg} ${config.text} px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 shadow-sm`}>
            {status === 'running' ? (
              <>
                <span className="inline-block w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                <span>{config.label}</span>
              </>
            ) : (
              <>
                <span className="text-sm">{config.icon}</span>
                <span>{config.label}</span>
              </>
            )}
          </div>

          {/* Run button */}
          <button
            onClick={() => onRun(scenario.name)}
            disabled={status === 'running'}
            className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed text-white px-4 py-1.5 rounded-lg font-semibold text-xs shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50"
          >
            {status === 'running' ? (
              <span className="flex items-center gap-2">
                <span className="inline-block w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                Running...
              </span>
            ) : (
              'Run'
            )}
          </button>
        </div>
      </div>

      {/* Content - only when expanded */}
      {isExpanded && (
        <div className="px-4 pb-4 space-y-4 border-t border-gray-700 pt-4">
        {/* Inputs section */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <div className="w-1 h-4 bg-blue-500 rounded-full"></div>
            <span className="text-xs font-bold text-blue-400 uppercase tracking-wide">Inputs</span>
          </div>
          <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-3 space-y-2">
            {scenario.inputs && scenario.inputs.map((input, idx) => (
              <div key={idx} className="flex items-start gap-3 text-sm text-gray-300">
                {/* Status indicator - aligned */}
                <div className="flex-shrink-0 w-5 h-5 flex items-center justify-center mt-0.5">
                  {status === 'completed' ? (
                    <div className="w-4 h-4 rounded-full bg-emerald-500 flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  ) : status === 'running' ? (
                    <div className="w-4 h-4 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin"></div>
                  ) : (
                    <div className="w-3 h-3 rounded-full border-2 border-gray-600"></div>
                  )}
                </div>
                {/* Input text */}
                <span className="flex-1">{input}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Expected section */}
        {scenario.profileExpectations && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-1 h-4 bg-emerald-500 rounded-full"></div>
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-wide">Expected</span>
            </div>
            <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-3 text-sm text-gray-300 leading-relaxed">
              {scenario.profileExpectations}
            </div>
          </div>
        )}

        {/* Result section - only when test is completed */}
        {result && status === 'completed' && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-1 h-4 rounded-full ${result.passed ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
              <span className={`text-xs font-bold uppercase tracking-wide ${result.passed ? 'text-emerald-400' : 'text-red-400'}`}>
                Result: {result.passed ? 'PASSED ✓' : 'FAILED ✗'}
              </span>
            </div>
            <div className={`border-2 rounded-lg p-4 ${result.passed ? 'bg-emerald-950/30 border-emerald-700' : 'bg-red-950/30 border-red-700'}`}>
              {/* Reasoning */}
              {result.reasoning && (
                <div className="mb-3">
                  <div className="text-xs font-semibold text-gray-400 mb-1">Reasoning:</div>
                  <div className="text-sm text-gray-300">{result.reasoning}</div>
                </div>
              )}

              {/* Actual profile */}
              {result.actual_profile && (
                <div className="mb-3">
                  <div className="text-xs font-semibold text-gray-400 mb-1">Actual Profile:</div>
                  <div className="text-sm text-gray-300 bg-gray-900/50 rounded p-2">{result.actual_profile}</div>
                </div>
              )}

              {/* Missing items */}
              {result.missing && result.missing.length > 0 && (
                <div className="mb-3">
                  <div className="text-xs font-semibold text-red-400 mb-1">Missing:</div>
                  <div className="text-sm text-red-300">
                    {result.missing.map((item, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <span>•</span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Unexpected items */}
              {result.unexpected && result.unexpected.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-yellow-400 mb-1">Unexpected:</div>
                  <div className="text-sm text-yellow-300">
                    {result.unexpected.map((item, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <span>•</span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Error */}
              {result.error && (
                <div className="text-sm text-red-300 bg-red-900/20 rounded p-2">
                  <strong>Error:</strong> {result.error}
                </div>
              )}
            </div>
          </div>
        )}
        </div>
      )}
    </div>
  );
}
