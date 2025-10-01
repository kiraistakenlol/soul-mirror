// Notes list with auto-refresh

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function NotesList() {
  const [notes, setNotes] = useState([]);
  const [count, setCount] = useState(0);
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
      setCount(data.count || 0);

      if (data.notes && Object.keys(data.notes).length > 0) {
        const notesList = Object.values(data.notes)
          .sort((a, b) => new Date(b.created) - new Date(a.created));
        setNotes(notesList);
      } else {
        setNotes([]);
      }
    } catch {
      setNotes([]);
    } finally {
      setLoading(false);
    }
  }

  // Refresh notes when needed (expose via ref or context)
  useEffect(() => {
    window.refreshNotes = loadNotes;
    return () => delete window.refreshNotes;
  }, []);

  return (
    <div className="bg-gray-900 rounded-lg p-6 h-full flex flex-col">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xl">📝</span>
        <h2 className="text-lg font-semibold text-white">
          Your Notes <span className="text-gray-400">({count})</span>
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {loading && notes.length === 0 ? (
          <div className="bg-gray-800 rounded p-4 text-gray-400 text-sm">
            Loading notes...
          </div>
        ) : notes.length === 0 ? (
          <div className="bg-gray-800 rounded p-4 text-gray-400 text-sm">
            No notes yet. Start sharing your thoughts!
          </div>
        ) : (
          notes.map((note) => (
            <div key={note.id} className="bg-gray-800 rounded p-4 hover:bg-gray-750 transition-colors">
              <div className="text-gray-200 text-sm mb-2 whitespace-pre-wrap">
                {note.content}
              </div>
              <div className="flex gap-3 text-xs text-gray-500">
                <span className="font-mono">ID: {note.id}</span>
                <span>Created: {new Date(note.created).toLocaleDateString()}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
