// View for browsing request history

import { useState, useEffect } from 'react';
import api from '../services/api';

export default function RequestsView() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchRequests = async () => {
    try {
      const data = await api.getRequests(100); // Fetch last 100 requests
      setRequests(data.requests || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch requests:', err);
      setError('Failed to load requests');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();

    if (autoRefresh) {
      const interval = setInterval(fetchRequests, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-white">📝 Request History</h2>
            <p className="text-gray-400 mt-1">Browse all requests and responses</p>
          </div>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-gray-300">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="w-4 h-4"
              />
              Auto-refresh
            </label>
            <button
              onClick={fetchRequests}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white font-medium transition-colors"
            >
              🔄 Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="text-center py-8 text-gray-400">Loading requests...</div>
        ) : error ? (
          <div className="text-center py-8 text-red-400">{error}</div>
        ) : requests.length === 0 ? (
          <div className="text-center py-8 text-gray-400">No requests found</div>
        ) : (
          <div className="space-y-4">
            {requests.map((request) => (
              <div
                key={request.id}
                className="bg-gray-900 rounded-lg p-6 border border-gray-800 hover:border-gray-700 transition-colors"
              >
                <div className="flex justify-between items-start mb-3">
                  <span className="text-xs text-gray-500">
                    ID: {request.id}
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatDate(request.created_at)}
                  </span>
                </div>

                <div className="mb-4">
                  <div className="text-sm font-semibold text-gray-400 mb-1">Request:</div>
                  <div className="text-white bg-gray-800 rounded p-3 font-mono text-sm">
                    {request.input}
                  </div>
                </div>

                {request.response && (
                  <div>
                    <div className="text-sm font-semibold text-gray-400 mb-1">Response:</div>
                    <div className="text-green-300 bg-gray-800 rounded p-3 font-mono text-sm">
                      {request.response}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}