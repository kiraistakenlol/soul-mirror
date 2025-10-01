// Tools list with expandable view

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Tools() {
  const [tools, setTools] = useState([]);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    loadTools();
  }, []);

  async function loadTools() {
    try {
      const data = await api.getTools();
      setTools(data.tools || []);
    } catch {
      setTools([]);
    }
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between text-left hover:bg-gray-800 rounded p-2 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">🛠️</span>
          <h3 className="text-sm font-semibold text-white">
            Available Tools <span className="text-gray-500">({tools.length})</span>
          </h3>
        </div>
        <span className="text-gray-400 text-xs">
          {expanded ? '▼' : '▶'}
        </span>
      </button>

      {expanded && (
        <div className="mt-3 space-y-2 pl-8">
          {tools.map((tool, idx) => (
            <div key={idx} className="bg-gray-800 rounded p-3 text-xs">
              <div className="font-mono text-blue-400 mb-1">{tool.name}</div>
              <div className="text-gray-400 mb-1">{tool.description}</div>
              {tool.parameters && (
                <div className="text-gray-500 font-mono text-[10px]">
                  ({tool.parameters.join(', ')})
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
