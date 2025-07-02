from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from src.llm.llm import get_llm_by_type
from src.config.logger import logger
from src.prompts.prompts import apply_prompt_template
from src.memory.memory_manager import MemoryManager
from src.graph.state import CineBrainState as State


# --- Node: Memory Extraction ---
def memory_extraction_node(state: State) -> Command[Literal["router"]]:
    """Extract relevant memory context from the last message and route to router."""
    logger.system_info("Running memory_extraction_node")
    if not state["messages"]:
        logger.system_info("No messages in state; skipping memory extraction.")
        return Command(goto="router")

    memory_manager = MemoryManager()
    last_message = state["messages"][-1]
    try:
        memory_context = memory_manager.extract_memory(last_message.content)
        if memory_context:
            logger.system_info(f"Memory context found: {memory_context}")
        else:
            logger.system_info("No relevant memory context found.")
        return Command(update={"memory_context": memory_context}, goto="router")
    except Exception as e:
        logger.workflow_error(f"Error during memory extraction: {e}")
        return Command(update={"memory_context": ""}, goto="router")

# --- Node: Router ---
def router_node(state: State) -> Command[Literal["conversation", "video", "audio"]]:
    """Route to the appropriate workflow based on user input or state."""
    logger.system_info("Running router_node")
    # Example: simple routing logic (customize as needed)
    workflow = state.get("workflow", "conversation")
    return Command(goto=workflow)

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
