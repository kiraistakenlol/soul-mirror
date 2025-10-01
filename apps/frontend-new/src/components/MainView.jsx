// Main application view with profile, notes, and chat

import { useState } from 'react';
import Profile from './Profile';
import NotesList from './NotesList';
import ResponseDisplay from './ResponseDisplay';
import ChatInput from './ChatInput';
import Tools from './Tools';
import ConversationHistory from './ConversationHistory';

export default function MainView() {
  const [latestResponse, setLatestResponse] = useState(null);

  return (
    <>
      <main className="max-w-7xl mx-auto p-6 pb-48">
        <div className="mb-6 space-y-4">
          <Tools />
          <ConversationHistory />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Profile */}
          <div className="lg:col-span-1">
            <Profile />
          </div>

          {/* Center: Notes */}
          <div className="lg:col-span-1 h-[calc(100vh-200px)]">
            <NotesList />
          </div>

          {/* Right: Latest Response */}
          <div className="lg:col-span-1">
            <ResponseDisplay response={latestResponse} />
          </div>
        </div>
      </main>

      <ChatInput onResponse={setLatestResponse} />
    </>
  );
}
