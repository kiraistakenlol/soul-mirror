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

  return (
    <div className="h-full flex flex-col">
      <div className="px-4 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-xl">💬</span>
          <span className="text-sm text-gray-300 font-medium">Latest Response</span>
        </div>
        {response && (
          <button
            onClick={copyToClipboard}
            className="text-xs bg-gray-800 hover:bg-blue-600 text-gray-300 hover:text-white px-3 py-1.5 rounded transition-colors"
          >
            {copied ? 'Copied!' : 'Copy'}
          </button>
        )}
      </div>
      <div className="px-4 pb-3 flex-1 overflow-y-auto">
        {!response ? (
          <div className="text-gray-400 text-sm">
            No responses yet. Start a conversation!
          </div>
        ) : (
          <div className="bg-gray-800 border-l-4 border-green-500 rounded p-3">
            <pre className="text-gray-300 text-xs font-mono whitespace-pre-wrap">
              {JSON.stringify(response, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
