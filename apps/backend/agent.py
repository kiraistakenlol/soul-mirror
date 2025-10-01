# LangGraph agent implementation using modern patterns
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from tools.notes import notes_manager

load_dotenv()

# Define tools that accept config parameter
@tool
def list_groups(config: RunnableConfig) -> str:
    """List all groups with their descriptions"""
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.list_groups(user_id)

@tool
def add_group(name: str, description: str, config: RunnableConfig) -> str:
    """Create a new group for organizing notes

    Args:
        name: Unique name for the group
        description: What this group is for
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.add_group(user_id, name, description)

@tool
def remove_group(group_id: str, config: RunnableConfig) -> str:
    """Remove a group and all its notes

    Args:
        group_id: The ID of the group to remove
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.remove_group(user_id, group_id)

@tool
def list_notes(group_id: str = None, config: RunnableConfig = None) -> str:
    """List all notes, optionally filtered by group

    Args:
        group_id: Optional group ID to filter notes
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.list_notes(user_id, group_id)

@tool
def add_note(content: str, group_id: str, config: RunnableConfig) -> str:
    """Add a note to a specific group

    Args:
        content: The content of the note to add
        group_id: The ID of the group to add the note to
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.add_note(user_id, content, group_id)

@tool
def remove_note(note_id: str, config: RunnableConfig) -> str:
    """Remove a note by its ID

    Args:
        note_id: The ID of the note to remove
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.remove_note(user_id, note_id)

# Collect all tools
tools = [list_groups, add_group, remove_group, list_notes, add_note, remove_note]

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

        # Build and compile graph once
        self.app = self._build_graph().compile()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""

        # Create the graph
        workflow = StateGraph(MessagesState)

        # Define the agent node that calls the LLM
        def call_model(state: MessagesState):
            messages = state["messages"]
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}

        # Define routing logic
        def should_continue(state: MessagesState) -> Literal["tools", "end"]:
            messages = state["messages"]
            last_message = messages[-1]

            # If the LLM makes a tool call, route to tools node
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            # Otherwise, end
            return "end"

        # Add nodes to the graph
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(tools))

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
    
    def process_input(self, user_input: str, user_id: str = "default") -> str:
        """Process user input through the agent"""

        # System prompt for the personal assistant
        system_msg = SystemMessage(content="""You are a personal assistant with a notebook organized into groups, where you remember everything about your user.

Your primary job is to learn about your user over time and provide personalized help based on what you know.

CORE PRINCIPLE: Always keep notes organized in groups. Before adding a note, find the right group or create one.

ORGANIZATION WORKFLOW:

1. Check existing groups with list_groups()
2. Before adding a note:
   - Find a group that fits the note's topic
   - If no suitable group exists, create one with add_group()
   - Then add the note to that group with add_note()
3. Keep groups focused and well-described

COMMON GROUPS TO CREATE:

- "Profile" - who the user is (personality, values, preferences)
- "Interests" - hobbies and things they enjoy
- "Work" - career, projects, professional life
- "Goals" - aspirations and things they're working towards
- "Tasks" - todos and reminders
- "Events" - appointments and scheduled things
- "People" - relationships and important people
- "Skills" - things they're learning

Create new groups when topics emerge that don't fit existing ones.

DECISION TREE FOR EVERY INPUT:

1. list_groups() to see what's organized
2. list_notes() to understand context
3. Analyze the input:
   - What topic does this relate to?
   - Is there a group for this? If not, create one
   - Does it reveal something about who they are? → Find/create appropriate group
   - Does it contradict existing info? → Remove old note, add new one
   - Is it temporary information? → Find/create Tasks or Events group
4. Use notes from relevant groups to personalize responses

EXAMPLES:

Input: "I love surfing"
Actions:
- list_groups() → see "Interests" group exists
- list_notes() → check for related notes
- add_note("Loves surfing", group_id="interests_group_id")
Response: "Got it! Added that you love surfing to your Interests."

Input: "I need to buy groceries tomorrow"
Actions:
- list_groups() → check if "Tasks" group exists
- If not: add_group("Tasks", "Todos and reminders")
- add_note("Buy groceries tomorrow", group_id="tasks_group_id")
Response: "Added to your Tasks!"

Input: "I actually don't like coffee anymore"
Actions:
- list_groups() → see groups
- list_notes() → find old coffee note
- remove_note(old_note_id)
- add_note("No longer likes coffee", group_id="profile_group_id")
Response: "Updated! Removed the old coffee preference."

CRITICAL RULES:
- Always list groups first to see organization
- Never add notes without a group - find one or create it
- Keep groups well-organized and clearly described
- Remove redundant or outdated notes
- Use groups to quickly find relevant context""")
        
        # Create the input message
        human_msg = HumanMessage(content=user_input)

        # Process with user_id in config
        result = self.app.invoke(
            {"messages": [system_msg, human_msg]},
            config={"configurable": {"user_id": user_id}}
        )
        
        # Extract the final response
        final_message = result["messages"][-1]
        
        # Return the content of the final message
        if hasattr(final_message, "content"):
            return final_message.content
        return str(final_message)
    
