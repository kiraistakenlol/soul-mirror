// Notes list organized by groups with auto-refresh

import { useEffect, useState } from 'react';
import api from '../services/api';
import { formatTimestamp } from '../utils/time';

export default function NotesList() {
  const [groups, setGroups] = useState({});
  const [loading, setLoading] = useState(true);
  const [expandedGroups, setExpandedGroups] = useState({});
  const [showRules, setShowRules] = useState({});

  useEffect(() => {
    loadNotes();
    const interval = setInterval(loadNotes, 10000);
    return () => clearInterval(interval);
  }, []);

  function toggleGroup(groupId) {
    setExpandedGroups(prev => ({
      ...prev,
      [groupId]: !prev[groupId]
    }));
  }

  function toggleRules(groupId) {
    setShowRules(prev => ({
      ...prev,
      [groupId]: !prev[groupId]
    }));
  }

  async function loadNotes() {
    try {
      setLoading(true);
      const data = await api.getNotes();
      setGroups(data.groups || {});
    } catch {
      setGroups({});
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    window.refreshNotes = loadNotes;
    return () => delete window.refreshNotes;
  }, []);

  const totalGroups = Object.keys(groups).length;
  const totalNotes = Object.values(groups).reduce((sum, group) =>
    sum + Object.keys(group.notes || {}).length, 0
  );

  return (
    <div className="bg-gray-900 rounded-lg p-4 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">📝</span>
        <h2 className="text-xl font-semibold text-white">
          Notes
          <span className="text-gray-500 text-sm ml-2">
            {totalGroups} groups · {totalNotes} notes
          </span>
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2">
        {loading && totalGroups === 0 ? (
          <div className="bg-gray-800 rounded p-4 text-gray-400 text-sm">
            Loading...
          </div>
        ) : totalGroups === 0 ? (
          <div className="bg-gray-800 rounded p-4 text-gray-400 text-sm">
            No groups yet. Start sharing your thoughts!
          </div>
        ) : (
          Object.entries(groups)
            .sort((a, b) => a[1].name.localeCompare(b[1].name))
            .map(([groupId, group]) => {
              const notes = group.notes || {};
              const notesArray = Object.values(notes).sort((a, b) =>
                new Date(b.created) - new Date(a.created)
              );

              const isExpanded = expandedGroups[groupId];

              return (
                <div key={groupId} className="bg-gray-800 rounded overflow-hidden">
                  <button
                    onClick={() => toggleGroup(groupId)}
                    className="w-full px-4 py-3 flex items-center gap-3 text-left hover:bg-gray-750 transition-colors"
                  >
                    <span className="text-base text-gray-500 flex-shrink-0">{isExpanded ? '▼' : '▶'}</span>
                    <h3 className="text-blue-400 font-medium text-lg flex-shrink-0">{group.name}</h3>
                    <span className="text-gray-600 text-base flex-shrink-0">({notesArray.length})</span>
                    <p className="text-gray-500 text-base flex-1 truncate">{group.description}</p>
                    {group.updated && (
                      <span className="text-gray-600 text-base flex-shrink-0" title={`Created: ${group.created}\nUpdated: ${group.updated}`}>
                        {formatTimestamp(group.updated)}
                      </span>
                    )}
                  </button>

                  {isExpanded && (
                    <div className="px-4 pb-4 space-y-3">
                      {group.custom_rules && (
                        <div>
                          <button
                            onClick={() => toggleRules(groupId)}
                            className="text-gray-500 hover:text-gray-400 text-sm px-3 py-1 transition-colors"
                          >
                            {showRules[groupId] ? '▼ Hide rules' : '▶ Show rules'}
                          </button>
                          {showRules[groupId] && (
                            <div className="bg-gray-750 rounded px-3 py-2 text-base text-gray-400 italic border-l-2 border-blue-600 mt-2">
                              {group.custom_rules}
                            </div>
                          )}
                        </div>
                      )}
                      {notesArray.length === 0 ? (
                        <div className="text-gray-500 text-base italic px-3 py-2">No notes</div>
                      ) : (
                        notesArray.map(note => (
                          <div key={note.id} className="bg-gray-750 rounded px-3 py-3 hover:bg-gray-700 transition-colors">
                            <div className="text-gray-200 text-lg whitespace-pre-wrap leading-relaxed mb-2">
                              {note.content}
                            </div>
                            {note.updated && (
                              <div className="text-gray-600 text-base" title={`Created: ${note.created}\nUpdated: ${note.updated}`}>
                                {formatTimestamp(note.updated)}
                              </div>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              );
            })
        )}
      </div>
    </div>
  );
}
