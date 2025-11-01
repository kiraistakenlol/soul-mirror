// Main application view with notes and chat

import NotesList from './NotesList';
import ChatInput from './ChatInput';
import ConversationHistory from './ConversationHistory';

export default function MainView() {
  return (
    <div className="h-full flex overflow-hidden">
      {/* Left column: Notes (50%) */}
      <div className="w-1/2 flex flex-col border-r border-gray-800">
        <div className="flex-1 overflow-y-auto">
          <NotesList />
        </div>
      </div>

      {/* Right column: Conversation + Input (50%) */}
      <div className="w-1/2 flex flex-col bg-gray-900">
        {/* Conversation - takes remaining space */}
        <div className="flex-1 overflow-y-auto py-4">
          <ConversationHistory />
        </div>

        {/* Input - fixed at bottom */}
        <div className="flex-shrink-0">
          <ChatInput />
        </div>
      </div>
    </div>
  );
}
