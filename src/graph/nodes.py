from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from src.llm.llm import get_llm_by_type
from src.config.logger import logger
from src.prompts.prompts import apply_prompt_template
from src.prompts.planner_module import RouterResponse
from src.memory.memory_manager import  get_memory_manager
from src.graph.state import CineBrainState as State
from src.agents.agents import create_agent
from src.tools.tools import get_tools


# --- Node: Memory Extraction ---
async def memory_extraction_node(state: State) -> Command[Literal["router","_end_"]]:
    """Extract relevant memory context from the last message and route to router."""
    logger.system_info("Running memory_extraction_node")
    if not state["messages"]:
        return Command(goto="_end_")
    memory_manager = await get_memory_manager()
    memories = await memory_manager.extract_memory(state["messages"][-1].content)
    if memories:
        memory_context = memory_manager.format_memories_for_prompt(memories)
        return Command(update={"memory_context": memory_context}, goto="router")
    else:
        return Command(goto="router")

# --- Node: Router ---
def router_node(state: State) -> Command[Literal["conversation", "video", "audio", "_end_"]]:
    """Route to the appropriate workflow based on user input or state."""
    logger.system_info("Running router_node")
    llm = get_llm_by_type("basic").with_structured_output(RouterResponse)
    prompt = apply_prompt_template("ROUTER_PROMPT", state["messages"])
    response = llm.invoke([HumanMessage(content=prompt)])
    if response.conversation:
        return Command(goto="conversation")
    elif response.video:
        return Command(goto="video")
    elif response.audio:
        return Command(goto="audio")
    else:
        return Command(goto="_end_")

# --- Node: Context Injection ---
def context_injection_node(state: State) -> dict:
    """Inject relevant context (e.g., activity, memory) into the state."""
    logger.system_info("Running context_injection_node")
    # Example: inject current activity (stub)
    current_activity = "writing"  # Replace with real context logic
    return {"current_activity": current_activity}

# --- Node: Conversation ---
def conversation_node(state: State, config: RunnableConfig) -> Command[Literal["summary"]]:
    """Handle conversation and generate AI response."""
    logger.system_info("Running conversation_node")
    llm = get_llm_by_type("basic")
    prompt = apply_prompt_template(state["messages"])
    response = llm.invoke([HumanMessage(content=prompt)])
    state["messages"].append(AIMessage(content=response.content))
    return Command(update={"messages": state["messages"]}, goto="summary")

# --- Node: Video ---
def video_node(state: State, config: RunnableConfig) -> Command[Literal["summary"]]:
    """Handle video generation or processing."""
    logger.system_info("Running video_node")
    llm = get_llm_by_type("tools")
    prompt = apply_prompt_template(state["messages"])
    response = llm.invoke([HumanMessage(content=prompt)])
    # Stub: video_path logic
    video_path = "generated_video.mp4"
    return Command(update={"video_path": video_path}, goto="summary")

# --- Node: Audio ---
def audio_node(state: State, config: RunnableConfig) -> Command[Literal["summary"]]:
    """Handle audio generation or processing."""
    logger.system_info("Running audio_node")
    llm = get_llm_by_type("tools")
    prompt = apply_prompt_template(state["messages"])
    response = llm.invoke([HumanMessage(content=prompt)])
    # Stub: audio_path logic
    audio_path = "generated_audio.mp3"
    return Command(update={"audio_path": audio_path}, goto="summary")

# --- Node: Summary ---
def summary_node(state: State, config: RunnableConfig) -> Command[Literal["store_memory"]]:
    """Summarize the conversation so far."""
    logger.system_info("Running summary_node")
    llm = get_llm_by_type("prompt")
    prompt = "Summarize the conversation so far."
    messages = state["messages"] + [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    return Command(update={"summary": response.content}, goto="store_memory")

# --- Node: Store Memory ---
def store_memory_node(state: State) -> Command[Literal["router"]]:
    """Store the summary or important information in memory."""
    logger.system_info("Running store_memory_node")
    # Stub: store summary in memory (customize as needed)
    summary = state.get("summary", "")
    logger.info(f"Storing summary: {summary}")
    return Command(goto="router")
