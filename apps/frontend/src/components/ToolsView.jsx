// Tools view organized by toolkit

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function ToolsView() {
  const [toolkits, setToolkits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTools();
  }, []);

  async function loadTools() {
    try {
      setLoading(true);
      const data = await api.getTools();
      setToolkits(data.toolkits || []);
    } catch {
      setToolkits([]);
    } finally {
      setLoading(false);
    }
  }

  const totalTools = toolkits.reduce((sum, tk) => sum + tk.tools.length, 0);

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex items-center gap-4 mb-6">
          <span className="text-4xl">🛠️</span>
          <h1 className="text-3xl font-semibold text-white">Available Tools</h1>
          <span className="text-gray-400 text-xl">({totalTools})</span>
        </div>

        {loading ? (
          <div className="bg-gray-900 rounded-lg p-8 text-center text-gray-400 text-lg">
            Loading tools...
          </div>
        ) : toolkits.length === 0 ? (
          <div className="bg-gray-900 rounded-lg p-8 text-center text-gray-400 text-lg">
            No tools available
          </div>
        ) : (
          <div className="space-y-8">
            {toolkits.map((toolkit, tkIdx) => (
              <div key={tkIdx}>
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-2xl">📓</span>
                  <h2 className="text-2xl font-semibold text-white">{toolkit.name}</h2>
                  <span className="text-gray-500 text-lg">({toolkit.tools.length})</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {toolkit.tools.map((tool, idx) => (
                    <div key={idx} className="bg-gray-900 rounded-lg p-6 border border-gray-800 hover:border-gray-700 transition-colors">
                      <div className="flex items-start gap-4">
                        <span className="text-3xl flex-shrink-0">🔧</span>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-mono text-blue-400 text-lg font-semibold mb-3">
                            {tool.name}
                          </h3>
                          <p className="text-gray-300 text-base mb-3 leading-relaxed">
                            {tool.description}
                          </p>
                          {tool.parameters && tool.parameters.length > 0 && (
                            <div className="bg-gray-800 rounded p-3 border border-gray-700">
                              <div className="text-gray-500 text-xs font-semibold mb-2">PARAMETERS:</div>
                              <div className="font-mono text-sm text-gray-400">
                                {tool.parameters.join(', ')}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
