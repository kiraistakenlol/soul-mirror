// Latest response display

import { useState } from 'react';

export default function ResponseDisplay({ response }) {
  const [copied, setCopied] = useState(false);

  async function copyToClipboard() {
    if (!response) return;

    try {
      await navigator.clipboard.writeText(JSON.stringify(response, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  }

  if (!response) {
    return (
      <div className="bg-gray-900 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span>💬</span>
          <span>Latest Response</span>
        </h2>
        <div className="text-gray-400 text-sm">
          No responses yet. Start a conversation!
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <span>💬</span>
          <span>Latest Response</span>
        </h2>

        <button
          onClick={copyToClipboard}
          className="text-xs bg-gray-800 hover:bg-blue-600 text-gray-300 hover:text-white px-3 py-1.5 rounded transition-colors"
        >
          {copied ? 'Copied!' : 'Copy JSON'}
        </button>
      </div>

      <div className="bg-gray-800 border-l-4 border-green-500 rounded p-4 overflow-x-auto">
        <pre className="text-gray-300 text-xs font-mono whitespace-pre-wrap">
          {JSON.stringify(response, null, 2)}
        </pre>
      </div>
    </div>
  );
}
