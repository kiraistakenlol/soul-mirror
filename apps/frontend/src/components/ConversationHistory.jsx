// Conversation history display for debugging

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function ConversationHistory() {
  const [history, setHistory] = useState([]);
  const [count, setCount] = useState(0);

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
    <div className="h-full flex flex-col">
      <div className="px-4 pb-3 flex-shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-2xl">💬</span>
          <span className="text-lg text-gray-300 font-medium">Conversation ({count})</span>
        </div>
      </div>

      <div className="px-4 overflow-y-auto flex-1">
        <div className="space-y-3">
          {count === 0 ? (
            <div className="text-gray-500 text-base italic">No active conversation</div>
          ) : (
            history.map((msg, idx) => (
              <div key={idx} className="bg-gray-800 rounded p-4 text-base">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">
                    {msg.type === 'HumanMessage' ? '👤' :
                     msg.type === 'AIMessage' ? '🤖' :
                     '⚙️'}
                  </span>
                  <span className={`font-semibold text-lg ${
                    msg.type === 'HumanMessage' ? 'text-blue-400' :
                    msg.type === 'AIMessage' ? 'text-green-400' :
                    'text-yellow-400'
                  }`}>
                    {msg.type === 'HumanMessage' ? 'User' :
                     msg.type === 'AIMessage' ? 'Assistant' :
                     msg.type}
                  </span>
                </div>
                <div className="text-gray-300 whitespace-pre-wrap leading-relaxed">
                  {typeof msg.content === 'string'
                    ? msg.content
                    : JSON.stringify(msg.content, null, 2)
                  }
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
