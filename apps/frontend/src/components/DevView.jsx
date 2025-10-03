// Developer admin panel
import { useState } from 'react';
import api from '../services/api';

export default function DevView() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleCreateGroups = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await api.createDefaultNoteGroups();
      setResult(response);
    } catch (error) {
      setResult({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full overflow-auto p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">⚙️ Developer Panel</h1>

        {/* Notes Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-6 border-b border-gray-800 pb-3">
            📝 Notes
          </h2>

          <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
            <h3 className="text-lg font-medium mb-4">Create Default Note Groups</h3>
            <p className="text-gray-400 mb-6">
              Initialize the default note groups (Self-Improvement, Health, Project Ideas, etc.)
            </p>

            <button
              onClick={handleCreateGroups}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700
                       disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
            >
              {loading ? 'Creating...' : 'Create Default Groups'}
            </button>

            {result && (
              <div className={`mt-6 p-4 rounded-lg ${
                result.error ? 'bg-red-900/20 border border-red-800' : 'bg-green-900/20 border border-green-800'
              }`}>
                {result.error ? (
                  <p className="text-red-400">❌ Error: {result.error}</p>
                ) : (
                  <div className="text-green-400">
                    <p className="font-medium mb-2">✅ Success!</p>
                    <ul className="text-sm space-y-1 ml-4">
                      {result.created?.length > 0 && (
                        <li>Created: {result.created.join(', ')}</li>
                      )}
                      {result.skipped?.length > 0 && (
                        <li>Skipped (already exist): {result.skipped.join(', ')}</li>
                      )}
                      <li>Total: {result.total}</li>
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
