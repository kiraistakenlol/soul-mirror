# LangGraph agent implementation using modern patterns
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from tools.notes import notes_manager
from tools.notebook_toolkit import NotebookToolkit
from tools.memory_toolkit import MemoryToolkit
from tools.general_toolkit import GeneralToolkit
from tools.responsibilities_toolkit import ResponsibilitiesToolkit
from tools.calendar_toolkit import CalendarToolkit
from tools.telegram_toolkit import TelegramToolkit
from tools.tts_toolkit import TTSToolkit
from tools.memory import memory_manager

load_dotenv()

# Initialize toolkits and get tools
notebook_toolkit = NotebookToolkit()
memory_toolkit = MemoryToolkit()
general_toolkit = GeneralToolkit()
responsibilities_toolkit = ResponsibilitiesToolkit()
calendar_toolkit = CalendarToolkit()
telegram_toolkit = TelegramToolkit()
tts_toolkit = TTSToolkit()
tools = (notebook_toolkit.get_tools() + memory_toolkit.get_tools() +
         general_toolkit.get_tools() + responsibilities_toolkit.get_tools() +
         calendar_toolkit.get_tools() + telegram_toolkit.get_tools() +
         tts_toolkit.get_tools())

class Agent:
    def __init__(self):
        # Initialize LLM based on provider
        provider = os.getenv("LLM_PROVIDER", "anthropic")

        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.llm = ChatOpenAI(model="gpt-5-nano-2025-08-07", temperature=0, api_key=api_key)
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self.llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0, api_key=api_key)

        # Bind tools to the LLM
        self.llm_with_tools = self.llm.bind_tools(tools)

        # Log tool schemas once at initialization
        print("\n📋 Tool Schemas Bound to LLM:")
        for tool in tools:
            print(f"\n  🔧 {tool.name}")
            print(f"     Description: {tool.description}")
            if hasattr(tool, 'args_schema') and tool.args_schema:
                schema = tool.args_schema.model_json_schema()
                if 'properties' in schema:
                    print(f"     Parameters:")
                    for param_name, param_info in schema['properties'].items():
                        if param_name != 'config':
                            param_type = param_info.get('type', 'unknown')
                            param_desc = param_info.get('description', '')
                            required = param_name in schema.get('required', [])
                            req_flag = " (required)" if required else " (optional)"
                            print(f"       - {param_name}: {param_type}{req_flag}")
                            if param_desc:
                                print(f"         {param_desc}")
        print()

        # Build and compile graph once
        self.app = self._build_graph().compile()

        # Store conversation history per user: {user_id: [messages]}
        self.conversation_history = {}

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""

        # Create the graph
        workflow = StateGraph(MessagesState)

        # Define the agent node that calls the LLM
        def call_model(state: MessagesState):
            messages = state["messages"]
            print("  🤖 Calling LLM...")

            # Log what's being sent to LLM
            print("  📤 Sending to LLM:")
            print(f"     Messages: {len(messages)} total")
            for i, msg in enumerate(messages):
                msg_type = type(msg).__name__
                content_preview = ""
                if hasattr(msg, 'content'):
                    content_preview = f": {msg.content}"
                print(f"       [{i}] {msg_type}{content_preview}")

            # Log tool schemas that are bound to LLM (only on first call)
            if not hasattr(self, '_tools_logged'):
                print(f"     Tools: {len(tools)} bound to LLM")
                for tool in tools:
                    print(f"       - {tool.name}: {tool.description}")
                self._tools_logged = True

            response = self.llm_with_tools.invoke(messages)

            if hasattr(response, 'content') and response.content:
                print(f"  💭 LLM response: {response.content[:100]}")
            elif hasattr(response, "tool_calls") and response.tool_calls:
                tool_summary = ", ".join([f"{tc['name']}({', '.join(f'{k}={v}' for k,v in tc['args'].items())})" for tc in response.tool_calls])
                print(f"  💭 LLM tool calls: {tool_summary}")
            else:
                print(f"  💭 LLM response: (empty)")

            return {"messages": [response]}

        # Custom tool node with logging
        def call_tools(state: MessagesState):
            # Call tools
            tool_node = ToolNode(tools)
            result = tool_node.invoke(state)

            # Log tool results
            if "messages" in result:
                for msg in result["messages"]:
                    if hasattr(msg, "content"):
                        content_preview = msg.content[:200] if len(msg.content) > 200 else msg.content
                        print(f"  ✅ Tool returned: {content_preview}")

            return result

        # Define routing logic
        def should_continue(state: MessagesState) -> Literal["tools", "end"]:
            messages = state["messages"]
            last_message = messages[-1]

            # If the LLM makes a tool call, route to tools node
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                tool_names = [tc["name"] for tc in last_message.tool_calls]
                print(f"  🔀 Routing to tools: {', '.join(tool_names)}")
                return "tools"
            # Otherwise, end
            print("  🔀 Routing to end")
            return "end"

        # Add nodes to the graph
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", call_tools)

        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )
        workflow.add_edge("tools", "agent")

        return workflow
    
    def process_input(self, user_input: str, user_id: str = "default", callbacks=None) -> str:
        """Process user input through the agent"""
        print(f"🚀 Starting agent flow for user={user_id}")

        # Load core memory for this user
        core_memory = memory_manager.get_core_memory(user_id)
        if core_memory:
            print(f"  🧠 Core memory loaded: {core_memory[:100]}...")
            memory_context = f"\n\nCore Memory (what you remember):\n{core_memory}\n"
        else:
            print(f"  🧠 No core memory yet")
            memory_context = "\n\nCore Memory: Empty (nothing remembered yet)\n"

        # System prompt for the personal assistant
        system_msg = SystemMessage(content=f"""You are a personal assistant. Use available tools to fulfill user requests ranging from simple tasks (groceries list) to complex workflows (generate Spanish text, convert to audio, send to Telegram channel). You can handle any combination of these tools to accomplish user goals - the examples below are just common patterns, not limitations.
{memory_context}

## AVAILABLE TOOLS

### NOTEBOOK - Structured information storage
What it does: Store and organize notes in topic-based groups
Tools:
  - list_groups() - view all groups
  - add_group(name, description, custom_rules?) - create new group
  - remove_group(group_id) - delete group and all its notes
  - list_notes(group_id?) - view notes (all or in specific group)
  - add_note(content, group_id) - add note to group
  - update_note(note_id, new_content) - modify existing note
  - remove_note(note_id) - delete note
  - search_notes(query) - find notes by keyword
  - move_note(note_id, new_group_id) - relocate note
  - get_groups_count() - count total groups
When to use: User wants to save information (recipes, meeting notes, lists). Check state with list_groups() first. Organize semantically. Follow group custom_rules if present. Translate to English before storing.
Examples: "save this recipe", "add milk to groceries", "update meeting notes"

### CORE MEMORY - Long-term user understanding
What it does: Store single text field of important context about user (preferences, habits, patterns)
Tools:
  - update_core_memory(new_content) - replace entire memory with new version
When to use: Learn significant information that affects future interactions. Always provide COMPLETE updated content (read existing from context above, incorporate new info, write full version).
Examples: "remember I'm learning Spanish", "I work with Roman", "I prefer mornings"
Don't use for: Transient tasks, simple reminders, detailed information (use Notebook instead)

### RESPONSIBILITIES - Workflow definitions
What it does: Store descriptions of recurring workflows/tasks that need to be executed
Tools:
  - list_responsibilities() - view all
  - add_responsibility(title, description) - create new (description = plain English: what, when, how)
  - update_responsibility(responsibility_id, title?, description?) - modify existing
  - remove_responsibility(responsibility_id) - delete
When to use: User requests recurring tasks requiring action/execution. These are your "job assignments" - define WHAT to do.
Examples: "send daily meditation quote at 7am", "generate weekly summary", "post Spanish lesson every morning"
Don't use for: One-time reminders (use Calendar directly), storing facts (use Notebook)

### CALENDAR - Event scheduling
What it does: Create, view, and manage scheduled events (one-time or recurring)
Tools:
  - add_calendar_event(scheduled_time, recurrence?, responsibility_id?, title?, description?) - schedule event
    • For one-time events: provide title (and optional description)
    • For recurring tasks: provide responsibility_id and recurrence pattern
  - list_calendar_events() - view all with next occurrence times
  - remove_calendar_event(event_id) - delete event
When to use: User wants something to happen at specific time(s). This defines WHEN to trigger.
Examples: "remind me tomorrow at 3pm" (one-time), "daily reminder at 7am" (recurring with responsibility)
Time format: "YYYY-MM-DD HH:MM" or "YYYY-MM-DD HH:MM:SS"
Recurrence: "daily", "weekly", "monthly", "yearly", or None

### TELEGRAM - Channel messaging
What it does: Send text messages and audio files to user's Telegram channels
Tools:
  - list_telegram_channels() - see available channels with chat_ids
  - send_telegram_message(chat_id, message) - send text-only message
  - send_audio_to_telegram(chat_id, file_id, caption?) - send audio file with optional text caption
When to use: User wants to post to Telegram. Always list_channels() first to get chat_id.
Examples: "send 'hello' to my channel", "post this audio to Spanish channel"
Important: send_audio_to_telegram sends actual audio file (from file_id), not text reference

### TTS - Text-to-speech generation
What it does: Convert text to audio files using ElevenLabs
Tools:
  - generate_speech(text, voice_id?) - generate audio, returns file_id
  - list_voices() - see available voices
When to use: User wants audio from text
Returns: file_id (use with send_audio_to_telegram to send to Telegram)
Examples: "create audio of this", "generate Spanish speech"

### GENERAL - Utilities
What it does: Helper functions
Tools:
  - get_current_datetime() - get current date/time

## COMMON WORKFLOWS

Simple reminder:
  "remind me tomorrow at 3pm" → add_calendar_event(scheduled_time="...", title="...")

Recurring task with Telegram:
  "send daily quote at 7am to my channel" →
  1. add_responsibility(title="Daily quote", description="Send motivational quote to Telegram at 7am")
  2. add_calendar_event(responsibility_id=X, scheduled_time="...", recurrence="daily")
  3. (when event triggers in future, use list_telegram_channels + send_telegram_message)

Audio to Telegram:
  "generate Spanish audio and send to channel" →
  1. generate_speech(text="...") → get file_id
  2. list_telegram_channels() → get chat_id
  3. send_audio_to_telegram(chat_id, file_id, caption="Spanish text")

Groceries list:
  "add milk to groceries" →
  1. list_groups() → find or create "Groceries" group
  2. add_note(content="milk", group_id=X)

Be direct and minimal. Only use tools when needed.""")

        # Get or initialize conversation history for this user
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        # Create the input message
        human_msg = HumanMessage(content=user_input)

        # Build messages: system + history + new input
        messages = [system_msg] + self.conversation_history[user_id] + [human_msg]
        print(f"  📚 Context: {len(self.conversation_history[user_id])} history messages")

        # Process with user_id in config and callbacks
        print("  ⚙️  Invoking graph...")
        config = {"configurable": {"user_id": user_id}}
        if callbacks:
            config["callbacks"] = callbacks
        result = self.app.invoke(
            {"messages": messages},
            config=config
        )

        # Extract all messages from result (includes history + new exchanges)
        result_messages = result["messages"]
        print(f"  📤 Graph returned {len(result_messages)} total messages")

        # Update conversation history with new exchanges (skip system message)
        # Store only the new human message and all subsequent messages
        self.conversation_history[user_id].append(human_msg)
        for msg in result_messages[len(messages):]:
            self.conversation_history[user_id].append(msg)

        # Extract the final response
        final_message = result_messages[-1]
        response_text = final_message.content if hasattr(final_message, "content") else str(final_message)
        print(f"✅ Agent complete: \"{response_text[:60]}{'...' if len(response_text) > 60 else ''}\"\n")

        # Return the content of the final message
        return response_text

    def reset_conversation(self, user_id: str = "default") -> str:
        """Reset conversation history"""
        history = self.conversation_history.get(user_id, [])

        if len(history) == 0:
            return "No conversation to reset."

        self.conversation_history[user_id] = []
        return "Conversation reset."
