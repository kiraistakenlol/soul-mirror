// Main application component

import { useState } from 'react';
import Header from './components/Header';
import Tabs from './components/Tabs';
import MainView from './components/MainView';
import TestsView from './components/TestsView';
import ProfilesView from './components/ProfilesView';

const TABS = [
  { id: 'main', label: 'Soul Mirror', icon: '🧠' },
  { id: 'tests', label: 'Tests', icon: '🧪' },
  { id: 'profiles', label: 'Profiles', icon: '👥' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('main');

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <Header />
      <Tabs tabs={TABS} activeTab={activeTab} onChange={setActiveTab} />

      {activeTab === 'main' && <MainView />}
      {activeTab === 'tests' && <TestsView />}
      {activeTab === 'profiles' && <ProfilesView />}
    </div>
  );
}
