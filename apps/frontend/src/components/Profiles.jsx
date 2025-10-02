// Browse all user profiles

import { useState, useEffect } from 'react';
import api from '../services/api';

export default function Profiles() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfiles();
  }, []);

  async function loadProfiles() {
    setLoading(true);
    try {
      const data = await api.getProfiles();
      setProfiles(data.profiles || []);
    } catch (error) {
      console.error('Failed to load profiles:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-gray-900 rounded-lg p-6 h-[calc(100vh-140px)] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">👥</span>
          <h2 className="text-lg font-semibold text-white">All Profiles</h2>
          {profiles.length > 0 && (
            <span className="text-gray-400 text-sm">({profiles.length} users)</span>
          )}
        </div>

        <button
          onClick={loadProfiles}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-4 py-2 rounded text-sm font-medium transition-colors"
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {loading ? (
          <div className="text-blue-400 text-sm">Loading profiles...</div>
        ) : profiles.length === 0 ? (
          <div className="text-gray-400 text-sm">No profiles found.</div>
        ) : (
          profiles.map((profile) => (
            <div
              key={profile.user_id}
              className="bg-gradient-to-br from-gray-800 to-gray-850 rounded-xl border-2 border-gray-700 hover:border-gray-600 transition-all duration-200 shadow-lg p-4"
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-bold text-white truncate">{profile.user_id}</h3>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs text-gray-400">
                      {profile.profile_count} profile notes
                    </span>
                    <span className="text-xs text-gray-500">•</span>
                    <span className="text-xs text-gray-400">
                      {profile.total_notes} total notes
                    </span>
                  </div>
                </div>
              </div>

              {profile.profile ? (
                <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-3 text-sm text-gray-300 leading-relaxed">
                  {profile.profile}
                </div>
              ) : (
                <div className="text-gray-500 text-sm italic">No profile data</div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
