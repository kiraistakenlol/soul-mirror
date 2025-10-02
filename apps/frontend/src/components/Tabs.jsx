// Tab navigation component

export default function Tabs({ tabs, activeTab, onChange }) {
  return (
    <div className="border-b border-gray-800">
      <div className="flex gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`px-8 py-4 font-medium text-base transition-colors ${
              activeTab === tab.id
                ? 'text-white border-b-2 border-blue-500 bg-gray-900'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-900/50'
            }`}
          >
            <span className="text-xl">{tab.icon}</span> {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}
