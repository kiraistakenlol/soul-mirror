// Tab navigation component

export default function Tabs({ tabs, activeTab, onChange }) {
  return (
    <div className="border-b border-gray-800">
      <div className="flex gap-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`px-6 py-3 font-medium text-sm transition-colors ${
              activeTab === tab.id
                ? 'text-white border-b-2 border-blue-500 bg-gray-900'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-900/50'
            }`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}
