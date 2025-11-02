// Memory view component - shows agent's core memory about user

import { useState, useEffect } from 'react';
import api from '../services/api';

export default function MemoryView() {
  const [memory, setMemory] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [clearing, setClearing] = useState(false);

  const loadMemory = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getMemory();
      setMemory(data.content || 'No memory yet');
    } catch (err) {
      setError(err.message);
      console.error('Failed to load memory:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClearMemory = async () => {
    try {
      setClearing(true);
      setError(null);
      await api.clearMemory();
      setShowConfirmModal(false);
      await loadMemory();
    } catch (err) {
      setError(err.message);
      console.error('Failed to clear memory:', err);
    } finally {
      setClearing(false);
    }
  };

  useEffect(() => {
    loadMemory();
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadMemory, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !memory) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        Loading memory...
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-950 p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-100 mb-2">Core Memory</h2>
          <p className="text-gray-400">
            What the agent remembers
          </p>
        </div>
        <button
          onClick={() => setShowConfirmModal(true)}
          disabled={memory === 'No memory yet'}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
        >
          Clear Memory
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-900/20 border border-red-500/50 rounded-lg text-red-400">
          {error}
        </div>
      )}

      <div className="flex-1 overflow-auto">
        <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
          {memory === 'No memory yet' ? (
            <p className="text-gray-500 italic">{memory}</p>
          ) : (
            <p className="text-gray-200 whitespace-pre-wrap leading-relaxed">
              {memory}
            </p>
          )}
        </div>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Auto-refreshes every 10 seconds
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-lg p-6 max-w-md w-full mx-4 border border-gray-800">
            <h3 className="text-xl font-bold text-gray-100 mb-4">
              Clear Memory?
            </h3>
            <p className="text-gray-400 mb-6">
              This will permanently delete all core memory. The agent will forget everything it has learned. This cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowConfirmModal(false)}
                disabled={clearing}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleClearMemory}
                disabled={clearing}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white rounded-lg transition-colors"
              >
                {clearing ? 'Clearing...' : 'Clear Memory'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
