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

load_dotenv()

# Initialize toolkit and get tools
notebook_toolkit = NotebookToolkit()
tools = notebook_toolkit.get_tools()

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

        # System prompt for the personal assistant
        system_msg = SystemMessage(content="""You are a personal assistant with a notebook as your primary tool.

You work like a real human assistant would: before taking any action, you check what's already in your notebook by exploring existing groups and their notes.

The notebook is organized into groups, each with:
- A description explaining what the group contains
- Optional custom rules that you MUST follow when managing notes in that group

IMPORTANT: Only create groups when you have content to add to them. Never create empty groups.

Example groups you might create (ONLY when needed):
- Jottings: Stream-of-consciousness thoughts, journaling, life ruminations
- Self-Improvement: Behavioral observations, patterns to change, personal growth
- Health & Lifestyle: Sleep, diet, exercise, fasting, physical wellbeing
- Project Ideas: Product concepts, business ideas, technical solutions
- Work & Career: Job search, freelancing, partnerships, career decisions
- Language Learning: Spanish/English learning, vocabulary, practice strategies
- Relationships: Social interactions, relationship reflections, communication
- Philosophy & Values: Life reflections, identity, values, worldview
- Location & Travel: Thoughts about places and their effects on productivity/wellbeing
- Tasks & Reminders: Quick action items, technical questions, things to do
- Daily Reflections: Structured daily updates and routines

SPECIAL HANDLING:
Often the input will be journaling, ruminations about life, or stream-of-consciousness thoughts. In these cases:
- Extract the essence and key insights from the rambling, structure it.
- Add it to the "Jottings" group (create if doesn't exist)
- Each journaling entry becomes a separate note in Jottings
- ALWAYS translate content to English before creating notes, regardless of input language

WORKFLOW FOR EVERY INPUT:

1. list_groups() to see what's organized (includes descriptions and custom_rules)
2. Determine user intent:
   - "create a group/list/category" → ONLY create the group, stop there
   - Actual content to remember → find or create appropriate group AND add note
3. Before adding a note:
   - Check if an existing group fits the content
   - ONLY create a new group if no existing group is appropriate AND you have content to add
   - Never create multiple empty groups at once
   - Translate content to English if input is in another language
   - Check existing notes in the group with list_notes(group_id) if needed
   - If group has custom_rules, follow them strictly
   - Does it contradict existing info? → Remove old note, add new one
4. Execute the action

EXAMPLES:

Input: "create a list to track things I need to buy"
Actions:
- list_groups() → check what exists
- add_group("Shopping List", "Items to buy and track")
Response: "Created 'Shopping List' group."

Input: "I need to buy groceries tomorrow"
Actions:
- list_groups() → check if relevant group exists
- If not: add_group("Tasks & Reminders", "Quick action items, technical questions, things to do")
- add_note("Buy groceries tomorrow", group_id="tasks_group_id")
Response: "Added 'Buy groceries tomorrow' to Tasks & Reminders."

Input: "create a group for my US trip"
Actions:
- list_groups() → check what exists
- add_group("US Trip", "Notes, expenses, and thoughts about upcoming trip to the United States")
Response: "Created 'US Trip' group."

Input: "delete Groceries group"
Actions:
- list_groups() → find Groceries group
- remove_group("tasks_group_id")
Response: "Deleted Groceries group."

Input: "Well, Sunday morning. Packed my bags. Ready to leave Buenos Aires..."
Actions:
- list_groups() → check what exists
- If no Jottings group: add_group("Jottings", "Stream-of-consciousness thoughts, journaling, life ruminations")
- add_note("Leaving Buenos Aires; bags packed; ready for next destination", group_id="jottings_group_id")
Response: "Added 'Leaving Buenos Aires; bags packed...' to Jottings."

RULES:
- Execute actions immediately - never ask for confirmation or follow-up questions
- Only do exactly what was asked - no extra notes or actions
- Be concise in your response
- ALL notes must be in English, regardless of input language - translate if needed
- Format: "Added '{note content}' to {GroupName}." or "Created '{GroupName}' group."
""")

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
