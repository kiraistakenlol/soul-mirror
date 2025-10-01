// Chat input with keyboard shortcuts

import { useState, useRef } from 'react';
import api from '../services/api';

export default function ChatInput({ onResponse }) {
  const [input, setInput] = useState('');
  const [processing, setProcessing] = useState(false);
  const [resetting, setResetting] = useState(false);
  const textareaRef = useRef(null);

  async function handleSubmit() {
    if (!input.trim() || processing) return;

    setProcessing(true);
    try {
      const data = await api.processInput(input);
      onResponse(data);
      setInput('');

      // Refresh profile and notes
      window.refreshProfile?.();
      window.refreshNotes?.();
    } catch (error) {
      onResponse({ error: error.message });
    } finally {
      setProcessing(false);
    }
  }

  async function handleReset() {
    if (resetting) return;

    setResetting(true);
    try {
      const data = await api.resetConversation();
      onResponse({
        response: data.summary,
        input: "Reset conversation"
      });

      // Refresh profile and notes to show the new Conversations note
      window.refreshProfile?.();
      window.refreshNotes?.();
    } catch (error) {
      onResponse({ error: error.message });
    } finally {
      setResetting(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    } else if (e.key === 'Escape') {
      setInput('');
    }
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur border-t border-gray-800 p-4 z-10">
      <div className="max-w-4xl mx-auto">
        <label className="text-sm text-gray-400 mb-2 block">
          💭 What's on your mind?
        </label>

        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a thought, idea, or goal. Enter = send, Shift+Enter = new line"
              className="w-full bg-gray-800 text-gray-100 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={3}
              disabled={processing}
            />
            <div className="text-xs text-gray-500 mt-2">
              Tip: Press <strong>Esc</strong> to clear
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={!input.trim() || processing}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
          >
            {processing ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>Process</span>
                <span>↵</span>
              </>
            )}
          </button>

          <button
            onClick={handleReset}
            disabled={resetting}
            className="bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2 text-sm"
            title="Summarize and reset conversation"
          >
            {resetting ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              </>
            ) : (
              <>
                <span>🔄</span>
                <span>Reset</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
