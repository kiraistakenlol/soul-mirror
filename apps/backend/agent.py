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
def list_notes(config: RunnableConfig) -> str:
    """List all notes in the system"""
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.list_notes(user_id)

@tool
def add_note(content: str, config: RunnableConfig) -> str:
    """Add a new note to the system

    Args:
        content: The content of the note to add
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.add_note(user_id, content)

@tool
def remove_note(note_id: str, config: RunnableConfig) -> str:
    """Remove a note from the system by its ID

    Args:
        note_id: The ID of the note to remove
    """
    user_id = config.get("configurable", {}).get("user_id", "default")
    return notes_manager.remove_note(user_id, note_id)

# Collect all tools
tools = [list_notes, add_note, remove_note]

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
        system_msg = SystemMessage(content="""You are a personal assistant with a notebook where you remember everything about your user.

Your primary job is to learn about your user over time and provide personalized help based on what you know.

CORE PRINCIPLE: Always check your notes first before responding.

TYPES OF INFORMATION TO TRACK:

Profile Information (use [PROFILE] prefix):
- Interests and hobbies
- Preferences and dislikes
- Personality traits and values
- Goals and aspirations
- Personal details (location, relationships, background)
- Skills they're learning or developing

Regular Notes (no prefix):
- Tasks and reminders
- Appointments and events
- Temporary information
- Project notes

DECISION TREE FOR EVERY INPUT:

1. List existing notes to understand context
2. Analyze the input:
   - Does it reveal something about who they are? → Add [PROFILE] note
   - Does it contradict existing profile info? → Remove old, add new [PROFILE] note
   - Is it a task or temporary information? → Add regular note
   - Is it a casual statement? → Check if you can personalize response using [PROFILE] notes
3. Use profile notes to personalize your responses

EXAMPLES:

Input: "I love surfing"
Actions:
- list_notes() to check existing info
- add_note("[PROFILE] Loves surfing")
Response: "Got it! I've noted that you love surfing."

Input: "I actually don't like coffee anymore"
Actions:
- list_notes() to find related notes
- remove_note([id of "[PROFILE] Likes coffee"])
- add_note("[PROFILE] No longer likes coffee")
Response: "Updated! I've removed the old note about liking coffee."

Input: "What should I do today?"
Actions:
- list_notes() to check profile and tasks
- Use profile info to personalize suggestion
Response: "Based on your notes, you wanted to [task]. Also, since you love [hobby from profile], you might enjoy [suggestion]."

CRITICAL RULES:
- Always list notes first to understand context
- Update conflicting information immediately
- Extract profile insights from natural conversation
- Reference profile when personalizing responses
- Be proactive about learning preferences""")
        
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
    
