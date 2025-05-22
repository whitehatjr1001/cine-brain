# nodes.py
from src.state import CineBrainState
from src.memory.memory_manager import MemoryManager
from src.tools import add_to_memory, search_memory, text_speech, box_office_predictor, imdb_api
from src.agents.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage,AIMessage


def router_node(state: CineBrainState, config: RunnableConfig):
    """
    Analyze the user's latest message and the conversation so far.
    """
    if not state["messages"]:
        return {}

    last_message = state["messages"][-1]

    return {"message": last_message}

def researcher_node(state: CineBrainState, config: RunnableConfig):
    """
    Analyze the user's latest message and the conversation so far.
    """
    if not state["messages"]:
        return {}

    last_message = state["messages"][-1]

    return {"message": last_message}

def writer_node(state: CineBrainState, config: RunnableConfig):
    """
    Analyze the user's latest message and the conversation so far.
    """
    if not state["messages"]:
        return {}

    last_message = state["messages"][-1]

    return {"message": last_message}

def dialogue_writer_node(state: CineBrainState, config: RunnableConfig):
    """
    Analyze the user's latest message and the conversation so far.
    """
    if not state["messages"]:
        return {}

    last_message = state["messages"][-1]

    return {"message": last_message}

def plot_consistency_node(state: CineBrainState, config: RunnableConfig):
    """
    Analyze the user's latest message and the conversation so far.
    """
    if not state["messages"]:
        return {}

    last_message = state["messages"][-1]

    return {"message": last_message}


def box_office_predictor_node(state: CineBrainState, config: RunnableConfig):
    """
    Analyze the user's latest message and the conversation so far.
    """
    if not state["messages"]:
        return {}

    last_message = state["messages"][-1]

    return {"message": last_message}


# ------------------------
# MEMORY EXTRACTION NODE
# ------------------------

async def memory_extraction_node(state: CineBrainState):
    """
    Extract and store important information from the last human message
    using the LLM-based Mem0-backed memory manager.
    """
    if not state["messages"]:
        return {}

    last_message = state["messages"][-1]

    memory_manager = MemoryManager(user_id="default_user")  # You can dynamically set user_id from state if needed
    await memory_manager.extract_and_store_memories(last_message)

    return {}  # No update to state directly here


# ------------------------
# MEMORY INJECTION NODE
# ------------------------
async def memory_injection_node(state: CineBrainState):
    """
    Retrieve relevant long-term memories based on recent context
    and inject them into the CineBrainState as memory_context.
    """
    if not state["messages"]:
        return {}

    # Create recent context from last 3 messages
    recent_context = " ".join([m.content for m in state["messages"][-3:]])

    memory_manager = MemoryManager(user_id="default_user")
    retrieved_memories = await memory_manager.retrieve_memories(recent_context)
    formatted_memory_context = memory_manager.format_memories_for_prompt(retrieved_memories)

    # Inject into state for downstream use in prompt construction
    return {"memory_context": formatted_memory_context}
