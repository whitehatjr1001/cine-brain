
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import CineBrainState as State
from .nodes import (
    memory_extraction_node,
    router_node,
    context_injection_node,
    conversation_node,
    video_node,
    audio_node,
    summary_node,
    store_memory_node,
)


def _build_base_graph():
    """Assemble all the nodes and the start/end markers."""
    g = StateGraph(State)

    # Define nodes
    g.add_node("memory_extraction", memory_extraction_node)
    g.add_node("router", router_node)
    g.add_node("context_injection", context_injection_node)
    g.add_node("conversation", conversation_node)
    g.add_node("video", video_node)
    g.add_node("audio", audio_node)
    g.add_node("summary", summary_node)
    g.add_node("store_memory", store_memory_node)

    # Define edges
    g.add_edge(START, "memory_extraction")

    # Memory Extraction decisions
    g.add_edge("memory_extraction", "router") # Both paths from memory_extraction go to router

    # Router decisions
    g.add_conditional_edges(
        "router",
        lambda state: state["workflow"],
        {
            "conversation": "context_injection",
            "video": "context_injection",
            "audio": "context_injection",
            "_end_": END, # If router decides to end
        },
    )

    # Context Injection to specific workflow nodes
    # The context_injection node is generic, and the next step depends on the workflow
    g.add_conditional_edges(
        "context_injection",
        lambda state: state["workflow"],
        {
            "conversation": "conversation",
            "video": "video",
            "audio": "audio",
        },
    )

    # Task Execution to Summary
    g.add_edge("conversation", "summary")
    g.add_edge("video", "summary")
    g.add_edge("audio", "summary")

    # Summary decisions
    g.add_conditional_edges(
        "summary",
        lambda state: "store_memory" if state.get("summary") and state["summary"].strip() else "_end_", # Assuming 'summary' determines if we go to store_memory or end
        {
            "store_memory": "store_memory",
            "_end_": END,
        },
    )
    # store memory goes back to router to allow for further interaction
    g.add_edge("store_memory", "router")

    return g


def build_graph_with_memory():
    """
    Build and compile the graph with a persistent MemorySaver.
    All state updates will be checkpointed.
    """
    memory = MemorySaver()
    base = _build_base_graph()
    return base.compile(checkpointer=memory)


def build_graph():
    """
    Build and compile the graph without any checkpointing.
    Suitable for ephemeral runs or testing.
    """
    return _build_base_graph().compile()


# default export for your orchestration engine
graph = build_graph_with_memory()


