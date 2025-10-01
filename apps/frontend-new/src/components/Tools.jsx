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
    <div className="bg-gray-900 rounded-lg border border-gray-800">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between text-left hover:bg-gray-800/50 rounded p-3 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">{expanded ? '▼' : '▶'}</span>
          <span className="text-xl">🛠️</span>
          <span className="text-sm text-gray-300 font-medium">Tools ({tools.length})</span>
        </div>
      </button>

      {expanded && (
        <div className="p-3 pt-0 space-y-2 border-t border-gray-800">
          {tools.map((tool, idx) => (
            <div key={idx} className="bg-gray-800 rounded p-3 text-sm">
              <div className="font-mono text-blue-400 mb-1 font-semibold">{tool.name}</div>
              <div className="text-gray-400 mb-1">{tool.description}</div>
              {tool.parameters && (
                <div className="text-gray-500 font-mono text-xs">
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
