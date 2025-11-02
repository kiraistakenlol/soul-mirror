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
from tools.memory import memory_manager

load_dotenv()

# Initialize toolkits and get tools
notebook_toolkit = NotebookToolkit()
memory_toolkit = MemoryToolkit()
general_toolkit = GeneralToolkit()
responsibilities_toolkit = ResponsibilitiesToolkit()
calendar_toolkit = CalendarToolkit()
telegram_toolkit = TelegramToolkit()
tools = (notebook_toolkit.get_tools() + memory_toolkit.get_tools() +
         general_toolkit.get_tools() + responsibilities_toolkit.get_tools() +
         calendar_toolkit.get_tools() + telegram_toolkit.get_tools())

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
        system_msg = SystemMessage(content=f"""You are a personal assistant. Help the user with tasks, reminders, scheduling, and information management.
{memory_context}
Your tools and their purposes:

1. CALENDAR - Schedule time-based tasks
   Purpose: Execute actions at specific times (reminders, recurring tasks)
   When to use: User asks to be reminded, do something at a time, or regularly
   One-time: add_calendar_event(scheduled_time="YYYY-MM-DD HH:MM", title="Remind about X", description="...")
   Recurring: create responsibility first, then add_calendar_event(responsibility_id=X, scheduled_time="...", recurrence="daily")

2. RESPONSIBILITIES - Track ongoing workflows
   Purpose: Store what you need to DO regularly (workflows that require execution)
   When to use: Recurring tasks that involve creating/generating content or complex actions
   Examples: "daily meditation text", "weekly summary", "monitor X and alert if Y"
   Not for: Simple recurring reminders (use calendar directly)
   Format: Plain English description of what, when, how

3. CORE MEMORY - Remember important context
   Purpose: Long-term memory of significant information about user, preferences, patterns
   When to use: Learning about user's habits, preferences, important context that affects future interactions
   Examples: "User is learning Spanish", "User works with Roman"
   Don't: Store transient information like one-time tasks or simple reminders
   How: Always provide COMPLETE new content (read existing → incorporate new info → write full updated version)
   Keep: Concise, relevant, structured

4. NOTEBOOK - Organized information storage
   Purpose: Store and organize information by topic (like a structured knowledge base)
   When to use: User shares information to remember, needs organized storage of facts/data
   Structure: Groups (by topic) containing notes
   Principles:
   - Check state first: list_groups() before acting
   - Semantic organization: group by meaning, not arbitrary categories
   - Cleanliness: delete outdated info, update instead of duplicate, no empty groups
   - Custom rules: each group can have rules - follow them strictly
   Examples: "Save this recipe", "Remember these meeting notes", "Track progress on project X"
   Don't: Use for simple reminders, transient tasks, or info that doesn't need organization
   Always: Translate content to English before storing

5. TELEGRAM - Send messages to Telegram channels
   Purpose: Post messages to user's Telegram channels
   When to use: User wants to send content to their Telegram channels, or when executing scheduled responsibilities that involve Telegram
   Tools:
   - list_telegram_channels() - See available channels (check this first)
   - send_telegram_message(chat_id, message) - Send message to a channel
   Examples: "Send 'Hello' to my Spanish channel", "Post this quote to my motivation channel"
   Note: User must tell you which channel to use, or you must list channels first to know the chat_id

When to use each tool:
- "Remind me tomorrow" → Calendar only
- "Send me daily quotes at 7am" → Responsibility + Calendar + Telegram
- "Remember I prefer mornings" → Core Memory
- "Save this recipe" → Notebook
- "Post this to my channel" → Telegram (list channels first if you don't know the chat_id)

Be direct and minimal. Only use tools when they serve the user's actual request.""")

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
