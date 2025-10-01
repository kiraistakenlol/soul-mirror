// User profile display

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Profile() {
  const [profile, setProfile] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      setLoading(true);
      const data = await api.getProfile();
      setProfile(data.profile || 'No profile information yet. Start sharing your thoughts to build your profile.');
    } catch {
      setProfile('Failed to load profile');
    } finally {
      setLoading(false);
    }
  }

  // Refresh profile when needed (expose via ref or context)
  useEffect(() => {
    window.refreshProfile = loadProfile;
    return () => delete window.refreshProfile;
  }, []);

  return (
    <div className="bg-gray-900 rounded-lg p-6 h-full">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xl">🧠</span>
        <h2 className="text-lg font-semibold text-white">Your Profile</h2>
      </div>

      <div className="bg-gray-800 border-l-4 border-blue-500 rounded p-4 max-h-[calc(100vh-200px)] overflow-y-auto">
        {loading ? (
          <div className="text-gray-400 text-sm">Loading profile...</div>
        ) : (
          <pre className="text-gray-300 text-sm whitespace-pre-wrap font-sans leading-relaxed">
            {profile}
          </pre>
        )}
      </div>
    </div>
  );
}
