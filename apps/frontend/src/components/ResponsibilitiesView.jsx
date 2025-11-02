// Responsibilities view - agent's internal workflows and tasks

import { useState, useEffect } from 'react';
import api from '../services/api';
import { formatTimestamp } from '../utils/time';

export default function ResponsibilitiesView() {
  const [responsibilities, setResponsibilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadResponsibilities = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getResponsibilities('default');
      setResponsibilities(data.responsibilities || []);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load responsibilities:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResponsibilities();
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadResponsibilities, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading && responsibilities.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        Loading responsibilities...
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-950 p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-100 mb-2">Responsibilities</h2>
        <p className="text-gray-400">
          Agent's internal workflows and recurring tasks
        </p>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-900/20 border border-red-500/50 rounded-lg text-red-400">
          {error}
        </div>
      )}

      <div className="flex-1 overflow-auto">
        {responsibilities.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            No responsibilities yet
          </div>
        ) : (
          <div className="space-y-4">
            {responsibilities.map((resp) => (
              <div
                key={resp.id}
                className="bg-gray-900 rounded-lg p-4 border border-gray-800 hover:border-gray-700 transition-colors"
              >
                <h3 className="text-lg font-semibold text-gray-100 mb-2">
                  {resp.title}
                </h3>
                <p className="text-gray-300 whitespace-pre-wrap mb-3">
                  {resp.description}
                </p>
                <div className="flex gap-4 text-sm text-gray-500">
                  <span title={new Date(resp.created_at).toLocaleString()}>
                    Created {formatTimestamp(resp.created_at)}
                  </span>
                  <span title={new Date(resp.updated_at).toLocaleString()}>
                    Updated {formatTimestamp(resp.updated_at)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-4 text-sm text-gray-500">
        {responsibilities.length} {responsibilities.length === 1 ? 'responsibility' : 'responsibilities'} • Auto-refreshes every 10 seconds
      </div>
    </div>
  );
}
