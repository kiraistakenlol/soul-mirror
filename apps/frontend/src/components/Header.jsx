// Header with connection status and tool count

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Header() {
  const [status, setStatus] = useState('connecting');
  const [toolCount, setToolCount] = useState(0);

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    loadTools();
  }, []);

  async function checkStatus() {
    try {
      const data = await api.getStatus();
      setStatus(data.status === 'healthy' ? 'connected' : 'disconnected');
    } catch {
      setStatus('disconnected');
    }
  }

  async function loadTools() {
    try {
      const data = await api.getTools();
      setToolCount(data.tools?.length || 0);
    } catch {
      setToolCount(0);
    }
  }

  return (
    <header className="bg-gray-900 border-b border-gray-800 px-6 py-5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-4xl">🧠</span>
          <h1 className="text-2xl font-semibold text-white">Soul Mirror</h1>
        </div>

        <div className="flex items-center gap-8 text-base text-gray-400">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${
              status === 'connected' ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="capitalize">{status}</span>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xl">⚡</span>
            <span>{toolCount} Tools</span>
          </div>
        </div>
      </div>
    </header>
  );
}
