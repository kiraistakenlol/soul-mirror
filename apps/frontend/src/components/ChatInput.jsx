// Chat input with keyboard shortcuts

import { useState, useRef } from 'react';
import api from '../services/api';

export default function ChatInput() {
  const [input, setInput] = useState('');
  const [processing, setProcessing] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState(null);
  const textareaRef = useRef(null);

  async function handleSubmit() {
    if (!input.trim() || processing) return;

    setProcessing(true);
    setError(null);

    const submittedInput = input;
    setInput(''); // Clear input immediately to allow new input

    try {
      await api.processInput(submittedInput);

      // Refresh notes and history
      window.refreshNotes?.();
      window.refreshHistory?.();
    } catch (error) {
      console.error('Failed to process input:', error);
      setError(error.message || 'Failed to process input');
      setInput(submittedInput); // Restore input on error
    } finally {
      setProcessing(false);
    }
  }

  async function handleReset() {
    if (resetting) return;

    setResetting(true);
    setError(null);
    try {
      await api.resetConversation();

      // Refresh notes and history
      window.refreshNotes?.();
      window.refreshHistory?.();
    } catch (error) {
      console.error('Failed to reset conversation:', error);
      setError(error.message || 'Failed to reset conversation');
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
    <div className="bg-gray-950 border-t border-gray-800 p-4">
        {error && (
          <div className="mb-3 bg-red-900/20 border border-red-600 text-red-400 px-4 py-3 rounded-lg flex items-center gap-2 text-base">
            <span className="text-xl">⚠️</span>
            <span>{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-400 hover:text-red-300 text-lg"
            >
              ✕
            </button>
          </div>
        )}
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="💭 Type a thought, idea, or goal... (Enter = send, Shift+Enter = new line, Esc = clear)"
              className="w-full bg-gray-900 text-gray-100 rounded-lg px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none border border-gray-700"
              rows={3}
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={!input.trim() || processing}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2 text-lg"
          >
            {processing ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <span>Process</span>
                <span className="text-xl">↵</span>
              </>
            )}
          </button>

          <button
            onClick={handleReset}
            disabled={resetting}
            className="bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:cursor-not-allowed text-white px-5 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2 text-lg"
            title="Reset conversation"
          >
            {resetting ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              </>
            ) : (
              <>
                <span className="text-xl">🔄</span>
                <span>Reset</span>
              </>
            )}
          </button>
        </div>
    </div>
  );
}
