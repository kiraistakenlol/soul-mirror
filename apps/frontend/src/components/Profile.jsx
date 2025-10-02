// Profile display with auto-refresh

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function Profile() {
  const [profile, setProfile] = useState('');
  const [count, setCount] = useState(0);

  useEffect(() => {
    loadProfile();
    const interval = setInterval(loadProfile, 10000);

    window.refreshProfile = loadProfile;

    return () => {
      clearInterval(interval);
      delete window.refreshProfile;
    };
  }, []);

  async function loadProfile() {
    try {
      const data = await api.getProfile();
      setProfile(data.profile);
      setCount(data.count);
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="px-4 py-3 flex-shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-xl">🧠</span>
          <span className="text-sm text-gray-300 font-medium">Profile ({count})</span>
        </div>
      </div>

      <div className="px-4 pb-3 flex-1 overflow-y-auto">
        {profile ? (
          <p className="text-sm text-gray-400 leading-relaxed">{profile}</p>
        ) : (
          <p className="text-sm text-gray-600 italic">No profile information yet.</p>
        )}
      </div>
    </div>
  );
}
