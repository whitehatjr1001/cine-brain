# nodes.py
from src.state import CineBrainState
from src.memory.memory_manager import MemoryManager
from src.tools import add_to_memory, search_memory, text_speech, box_office_predictor, imdb_api
from src.agents.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.runnables import Command

def coordinator_node(state: CineBrainState, config: RunnableConfig):
    """
    Analyze the user's latest message and the conversation so far.
    """
    if not state["messages"]:
        return {}

    last_message = state["messages"][-1]

    return {"message": last_message}

def researcher_node(state: CineBrainState, config: RunnableConfig) -> Command(Literal["research_team"]):
    """
    Analyze the user's latest message and the conversation so far.
    """
    if not state["messages"]:
        return {}

    last_message = state["messages"][-1]

    return {"message": last_message}
def reserch_team_node(state: CineBrainState, config: RunnableConfig) -> Command(Literal["writer_node","dialogue_writer_node","plot_consistency_node","box_office_predictor_node"]):
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

async def _setup_and_execute_agent_step(
    state: State,
    config: RunnableConfig,
    agent_type: str,
    default_tools: list,
) -> Command[Literal["research_team"]]:
    """Helper function to set up an agent with appropriate tools and execute a step.

    This function handles the common logic for both researcher_node and coder_node:
    1. Configures MCP servers and tools based on agent type
    2. Creates an agent with the appropriate tools or uses the default agent
    3. Executes the agent on the current step

    Args:
        state: The current state
        config: The runnable config
        agent_type: The type of agent ("researcher" or "coder")
        default_tools: The default tools to add to the agent

    Returns:
        Command to update state and go to research_team
    """
    configurable = Configuration.from_runnable_config(config)
    mcp_servers = {}
    enabled_tools = {}

    # Extract MCP server configuration for this agent type
    if configurable.mcp_settings:
        for server_name, server_config in configurable.mcp_settings["servers"].items():
            if (
                server_config["enabled_tools"]
                and agent_type in server_config["add_to_agents"]
            ):
                mcp_servers[server_name] = {
                    k: v
                    for k, v in server_config.items()
                    if k in ("transport", "command", "args", "url", "env")
                }
                for tool_name in server_config["enabled_tools"]:
                    enabled_tools[tool_name] = server_name

    # Create and execute agent with MCP tools if available
    if mcp_servers:
        async with MultiServerMCPClient(mcp_servers) as client:
            loaded_tools = default_tools[:]
            for tool in client.get_tools():
                if tool.name in enabled_tools:
                    tool.description = (
                        f"Powered by '{enabled_tools[tool.name]}'.\n{tool.description}"
                    )
                    loaded_tools.append(tool)
            agent = create_agent(agent_type, agent_type, loaded_tools, agent_type)
            return await _execute_agent_step(state, agent, agent_type)
    else:
        # Use default tools if no MCP servers are configured
        agent = create_agent(agent_type, agent_type, default_tools, agent_type)
        return await _execute_agent_step(state, agent, agent_type)
