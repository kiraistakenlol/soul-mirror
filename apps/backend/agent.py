# LangGraph agent implementation using modern patterns
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from tools.notes import list_all_notes, add_new_note, remove_note_by_id

load_dotenv()

# Define tools using the @tool decorator
@tool
def list_notes() -> str:
    """List all notes in the system"""
    return list_all_notes()

@tool
def add_note(content: str) -> str:
    """Add a new note to the system
    
    Args:
        content: The content of the note to add
    """
    return add_new_note(content)

@tool
def remove_note(note_id: str) -> str:
    """Remove a note from the system by its ID
    
    Args:
        note_id: The ID of the note to remove
    """
    return remove_note_by_id(note_id)

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
        
        # Create the graph
        self.graph = self._build_graph()
        
        # Compile the graph without memory/checkpointing
        self.app = self.graph.compile()
    
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
    
    def process_input(self, user_input: str, thread_id: str = "default") -> str:
        """Process user input through the agent"""
        
        # Always add system message for consistent behavior
        system_msg = SystemMessage(content="""
        
You are a personal assistant that uses notes to remember everything about your user.

CRITICAL: Always prefix personal information notes with [PROFILE]

PERSONAL INFORMATION (always use [PROFILE] prefix):
- Interests, hobbies, likes/dislikes (e.g., "[PROFILE] User likes lemons and surfing")
- Personality traits, values, beliefs (e.g., "[PROFILE] User is detail-oriented and values efficiency")  
- Goals, aspirations, learning objectives (e.g., "[PROFILE] User learning Spanish")
- Personal details: location, background, relationships (e.g., "[PROFILE] User lives in Barcelona")

REGULAR NOTES (no prefix needed):
- Tasks, reminders, appointments (e.g., "Call mom tomorrow")
- Temporary information, events (e.g., "Meeting at 3pm today")
- Project notes, research (e.g., "Review documentation")

WORKFLOW:
1. FIRST: Check existing notes for related information
2. If input contradicts existing [PROFILE] notes → remove the old note and add new one
3. If input reveals new personal info → create [PROFILE] note
4. If input is a task/reminder → create regular note  
5. Check existing [PROFILE] notes to personalize responses
6. Always consider: "Does this tell me something about who this person is?"

EXAMPLES:
- "I love surfing" → "[PROFILE] User loves surfing"
- "Add note about groceries" → "Buy groceries"
- "I'm learning Spanish" → "[PROFILE] User learning Spanish"
- "I don't want to learn guitar anymore" → Remove old "[PROFILE] User wants to learn guitar" + Add "[PROFILE] User no longer interested in learning guitar"

IMPORTANT: When information changes or contradicts existing notes, always remove the outdated note first, then add the updated information.

Be consistent with [PROFILE] prefixes for all personal information.""")
        
        # Create the input message
        human_msg = HumanMessage(content=user_input)
        
        # Process without any config (no memory/threading needed)
        result = self.app.invoke(
            {"messages": [system_msg, human_msg]}
        )
        
        # Extract the final response
        final_message = result["messages"][-1]
        
        # Return the content of the final message
        if hasattr(final_message, "content"):
            return final_message.content
        return str(final_message)
    
