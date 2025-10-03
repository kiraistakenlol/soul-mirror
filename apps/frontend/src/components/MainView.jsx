// Main application view with notes and chat

import NotesList from './NotesList';
import ChatInput from './ChatInput';
import ConversationHistory from './ConversationHistory';

export default function MainView() {
  return (
    <div className="h-full flex overflow-hidden">
      {/* Left column: Notes + Input */}
      <div className="flex-1 flex flex-col border-r border-gray-800">
        {/* Notes - takes remaining space */}
        <div className="flex-1 overflow-y-auto">
          <NotesList />
        </div>

        {/* Input - fixed at bottom of notes column */}
        <div className="flex-shrink-0">
          <ChatInput />
        </div>
      </div>

      {/* Right sidebar (30%) - Conversation History */}
      <div className="w-[30%] flex flex-col bg-gray-900 py-4">
        <ConversationHistory />
      </div>
    </div>
  );
}
