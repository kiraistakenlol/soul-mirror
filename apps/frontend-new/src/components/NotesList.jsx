// Notes list organized by groups with auto-refresh

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function NotesList() {
  const [groups, setGroups] = useState({});
  const [notes, setNotes] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNotes();
    const interval = setInterval(loadNotes, 10000);
    return () => clearInterval(interval);
  }, []);

  async function loadNotes() {
    try {
      setLoading(true);
      const data = await api.getNotes();
      setGroups(data.groups || {});
      setNotes(data.notes || {});
    } catch {
      setGroups({});
      setNotes({});
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    window.refreshNotes = loadNotes;
    return () => delete window.refreshNotes;
  }, []);

  // Organize notes by group
  const notesByGroup = {};
  Object.values(notes).forEach(note => {
    const groupId = note.group_id || 'ungrouped';
    if (!notesByGroup[groupId]) notesByGroup[groupId] = [];
    notesByGroup[groupId].push(note);
  });

  // Sort notes within each group by created date
  Object.keys(notesByGroup).forEach(groupId => {
    notesByGroup[groupId].sort((a, b) => new Date(b.created) - new Date(a.created));
  });

  const totalNotes = Object.keys(notes).length;
  const totalGroups = Object.keys(groups).length;

  return (
    <div className="bg-gray-900 rounded-lg p-6 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xl">📝</span>
        <h2 className="text-lg font-semibold text-white">
          Notes
          <span className="text-gray-400 text-sm ml-2">
            {totalGroups} groups · {totalNotes} notes
          </span>
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4">
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
              const groupNotes = notesByGroup[groupId] || [];
              return (
                <div key={groupId} className="bg-gray-800 rounded-lg p-4">
                  <div className="mb-3 pb-2 border-b border-gray-700">
                    <h3 className="text-white font-semibold text-sm">{group.name}</h3>
                    <p className="text-gray-400 text-xs mt-1">{group.description}</p>
                    <span className="text-gray-500 text-xs">{groupNotes.length} notes</span>
                  </div>

                  <div className="space-y-2">
                    {groupNotes.length === 0 ? (
                      <div className="text-gray-500 text-xs italic">No notes in this group</div>
                    ) : (
                      groupNotes.map(note => (
                        <div key={note.id} className="bg-gray-750 rounded p-3 hover:bg-gray-700 transition-colors">
                          <div className="text-gray-200 text-xs mb-1 whitespace-pre-wrap">
                            {note.content}
                          </div>
                          <div className="text-xs text-gray-600 font-mono">
                            {note.id}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              );
            })
        )}
      </div>
    </div>
  );
}
