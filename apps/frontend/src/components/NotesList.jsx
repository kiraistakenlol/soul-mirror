// Notes list organized by groups with auto-refresh

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function NotesList() {
  const [groups, setGroups] = useState({});
  const [loading, setLoading] = useState(true);
  const [expandedGroups, setExpandedGroups] = useState({});

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
    <div className="bg-gray-900 rounded-lg p-6 h-full flex flex-col">
      <div className="flex items-center gap-3 mb-6">
        <span className="text-3xl">📝</span>
        <h2 className="text-2xl font-semibold text-white">
          Notes
          <span className="text-gray-400 text-base ml-3">
            {totalGroups} groups · {totalNotes} notes
          </span>
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto space-y-5">
        {loading && totalGroups === 0 ? (
          <div className="bg-gray-800 rounded p-6 text-gray-400 text-base">
            Loading...
          </div>
        ) : totalGroups === 0 ? (
          <div className="bg-gray-800 rounded p-6 text-gray-400 text-base">
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
                <div key={groupId} className="bg-gray-800 rounded-lg p-5">
                  <button
                    onClick={() => toggleGroup(groupId)}
                    className="w-full mb-4 pb-3 border-b border-gray-700 flex items-center gap-4 text-left hover:opacity-80 transition-opacity"
                  >
                    <span className="text-lg flex-shrink-0">{isExpanded ? '▼' : '▶'}</span>
                    <h3 className="text-blue-400 font-semibold text-lg flex-shrink-0">{group.name}</h3>
                    <p className="text-gray-400 text-sm flex-1 truncate">{group.description}</p>
                    <span className="text-gray-500 text-sm flex-shrink-0">{notesArray.length} notes</span>
                  </button>

                  {isExpanded && (
                    <div className="space-y-3">
                      {group.custom_rules && (
                        <div className="bg-gray-750 rounded p-3 mb-3 text-sm text-gray-400 italic border-l-2 border-blue-500">
                          {group.custom_rules}
                        </div>
                      )}
                      {notesArray.length === 0 ? (
                        <div className="text-gray-500 text-sm italic">No notes in this group</div>
                      ) : (
                        notesArray.map(note => (
                          <div key={note.id} className="bg-gray-750 rounded p-4 hover:bg-gray-700 transition-colors">
                            <div className="text-gray-100 text-base mb-2 whitespace-pre-wrap leading-relaxed">
                              {note.content}
                            </div>
                            <div className="text-xs text-gray-600 font-mono">
                              {note.id}
                            </div>
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
