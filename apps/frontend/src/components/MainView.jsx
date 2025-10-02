// Main application view with profile, notes, and chat

import Profile from './Profile';
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

      {/* Right sidebar (30%) - Profile, Conversation */}
      <div className="w-[30%] flex flex-col bg-gray-900">
        {/* Profile - 15% of right sidebar */}
        <div className="h-[15%] border-b border-gray-800 overflow-hidden">
          <Profile />
        </div>

        {/* Conversation History - 85% of right sidebar */}
        <div className="h-[85%] py-4">
          <ConversationHistory />
        </div>
      </div>
    </div>
  );
}
