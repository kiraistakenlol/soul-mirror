// Conversation history display for debugging

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function ConversationHistory() {
  const [history, setHistory] = useState([]);
  const [count, setCount] = useState(0);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    loadHistory();
    const interval = setInterval(loadHistory, 5000);
    return () => clearInterval(interval);
  }, []);

  async function loadHistory() {
    try {
      const data = await api.getConversationHistory();
      setHistory(data.messages || []);
      setCount(data.message_count || 0);
    } catch {
      setHistory([]);
      setCount(0);
    }
  }

  useEffect(() => {
    window.refreshHistory = loadHistory;
    return () => delete window.refreshHistory;
  }, []);

  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between text-left hover:bg-gray-800 rounded p-2 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">💬</span>
          <h3 className="text-sm font-semibold text-white">
            Conversation History <span className="text-gray-500">({count} messages)</span>
          </h3>
        </div>
        <span className="text-gray-400 text-xs">
          {expanded ? '▼' : '▶'}
        </span>
      </button>

      {expanded && (
        <div className="mt-3 space-y-2 pl-8 max-h-96 overflow-y-auto">
          {count === 0 ? (
            <div className="text-gray-500 text-xs italic">No active conversation</div>
          ) : (
            history.map((msg, idx) => (
              <div key={idx} className="bg-gray-800 rounded p-3 text-xs">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`font-semibold ${
                    msg.type === 'HumanMessage' ? 'text-blue-400' :
                    msg.type === 'AIMessage' ? 'text-green-400' :
                    'text-yellow-400'
                  }`}>
                    {msg.type === 'HumanMessage' ? '👤 User' :
                     msg.type === 'AIMessage' ? '🤖 Assistant' :
                     '⚙️ ' + msg.type}
                  </span>
                </div>
                <div className="text-gray-300 whitespace-pre-wrap">
                  {typeof msg.content === 'string'
                    ? msg.content.substring(0, 200) + (msg.content.length > 200 ? '...' : '')
                    : JSON.stringify(msg.content).substring(0, 200)
                  }
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
