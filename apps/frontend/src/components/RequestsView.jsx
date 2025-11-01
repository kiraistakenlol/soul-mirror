// View for browsing request history

import { useState, useEffect } from 'react';
import api from '../services/api';

export default function RequestsView() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [expandedTraces, setExpandedTraces] = useState({});
  const [copiedId, setCopiedId] = useState(null);

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

  const toggleTraces = (requestId) => {
    setExpandedTraces(prev => ({
      ...prev,
      [requestId]: !prev[requestId]
    }));
  };

  const copyRequestAsJson = (request) => {
    const json = JSON.stringify(request, null, 2);
    navigator.clipboard.writeText(json).then(() => {
      setCopiedId(request.id);
      setTimeout(() => setCopiedId(null), 2000);
    }).catch(err => {
      console.error('Failed to copy:', err);
    });
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
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => copyRequestAsJson(request)}
                      className={`text-xs px-2 py-1 rounded transition-colors ${
                        copiedId === request.id
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-800 hover:bg-gray-700 text-gray-300'
                      }`}
                      title="Copy as JSON"
                    >
                      {copiedId === request.id ? '✓ Copied' : '📋 Copy JSON'}
                    </button>
                    <span className="text-xs text-gray-500">
                      {formatDate(request.created_at)}
                    </span>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="text-sm font-semibold text-gray-400 mb-1">Request:</div>
                  <div className="text-white bg-gray-800 rounded p-3 font-mono text-sm">
                    {request.input}
                  </div>
                </div>

                {request.response && (
                  <div className="mb-4">
                    <div className="text-sm font-semibold text-gray-400 mb-1">Response:</div>
                    <div className="text-green-300 bg-gray-800 rounded p-3 font-mono text-sm">
                      {request.response}
                    </div>
                  </div>
                )}

                {request.llm_traces && request.llm_traces.length > 0 && (
                  <div>
                    <button
                      onClick={() => toggleTraces(request.id)}
                      className="flex items-center gap-2 text-sm font-semibold text-blue-400 hover:text-blue-300 transition-colors mb-2"
                    >
                      <span>{expandedTraces[request.id] ? '▼' : '▶'}</span>
                      <span>LLM Traces ({request.llm_traces.length})</span>
                    </button>

                    {expandedTraces[request.id] && (
                      <div className="space-y-3 mt-3">
                        {request.llm_traces.map((trace, idx) => (
                          <div key={idx} className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                            <div className="text-xs text-gray-500 mb-2">
                              Trace #{idx + 1} • {trace.model}
                            </div>

                            {/* Messages sent to LLM */}
                            {trace.messages && (
                              <div className="mb-3">
                                <div className="text-xs font-semibold text-purple-400 mb-1">Messages:</div>
                                <div className="space-y-2">
                                  {trace.messages[0]?.map((msg, msgIdx) => (
                                    <div key={msgIdx} className="bg-gray-900 rounded p-2">
                                      <div className="text-xs text-gray-500 mb-1">{msg.role}</div>
                                      <div className="text-xs text-gray-300 font-mono whitespace-pre-wrap">
                                        {typeof msg.content === 'string'
                                          ? msg.content
                                          : JSON.stringify(msg.content, null, 2)}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Response from LLM */}
                            {trace.response && (
                              <div>
                                <div className="text-xs font-semibold text-green-400 mb-1">Response:</div>
                                <div className="space-y-2">
                                  {trace.response[0]?.map((resp, respIdx) => (
                                    <div key={respIdx} className="bg-gray-900 rounded p-2">
                                      {resp.role && (
                                        <div className="text-xs text-gray-500 mb-1">{resp.role}</div>
                                      )}
                                      {resp.content && (
                                        <div className="text-xs text-green-300 font-mono whitespace-pre-wrap mb-2">
                                          {resp.content}
                                        </div>
                                      )}
                                      {resp.tool_calls && resp.tool_calls.length > 0 && (
                                        <div className="mt-2">
                                          <div className="text-xs text-yellow-400 mb-1">Tool Calls:</div>
                                          {resp.tool_calls.map((tc, tcIdx) => (
                                            <div key={tcIdx} className="text-xs text-yellow-300 font-mono bg-gray-950 rounded p-2 mb-1">
                                              <span className="text-yellow-400">{tc.name}</span>(
                                              {JSON.stringify(tc.args, null, 2)}
                                              )
                                            </div>
                                          ))}
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
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