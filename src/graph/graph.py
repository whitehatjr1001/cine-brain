
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import ChatAgentState
from .nodes import (
    coordinator_node,
    planner_node,
    human_feedback_node,
    team_router_node,
    research_team_node,
    resolution_team_node,
    reporter_node,
)


def _build_base_graph():
    """Assemble all the nodes and the start/end markers."""
    g = StateGraph(ChatAgentState)

    # entry point
    g.add_edge(START, "coordinator")
    g.add_node("coordinator", coordinator_node)

    # planning
    g.add_node("planner", planner_node)

    # human feedback
    g.add_node("human_feedback", human_feedback_node)

    # team router → two possible branches
    g.add_node("team_router", team_router_node)

    # research branch
    g.add_node("research_team", research_team_node)

    # resolution branch
    g.add_node("resolution_team", resolution_team_node)

    # final reporter
    g.add_node("reporter", reporter_node)
    g.add_edge("reporter", END)

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


