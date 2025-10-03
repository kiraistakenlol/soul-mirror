// Main application component

import { useState } from 'react';
import Header from './components/Header';
import Tabs from './components/Tabs';
import MainView from './components/MainView';
import ToolsView from './components/ToolsView';
import TestsView from './components/TestsView';

const TABS = [
  { id: 'main', label: 'Soul Mirror', icon: '🧠' },
  { id: 'tools', label: 'Tools', icon: '🛠️' },
  { id: 'tests', label: 'Tests', icon: '🧪' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('main');

  return (
    <div className="h-screen bg-gray-950 text-gray-100 flex flex-col overflow-hidden">
      <Header />
      <Tabs tabs={TABS} activeTab={activeTab} onChange={setActiveTab} />

      <div className="flex-1 overflow-hidden">
        {activeTab === 'main' && <MainView />}
        {activeTab === 'tools' && <ToolsView />}
        {activeTab === 'tests' && <TestsView />}
      </div>
    </div>
  );
}
