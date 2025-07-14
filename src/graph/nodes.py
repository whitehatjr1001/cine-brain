from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from src.llm.llm import get_llm_by_type
from src.config.logger import logger
from src.prompts.prompts import apply_prompt_template
from src.prompts.planner_module import RouterResponse, ComplexityAnalysis, ContextForGeneration, MemoryStorageDecision
from src.memory.memory_manager import  get_memory_manager
from src.graph.state import CineBrainState as State
from src.agents.agents import create_agent
from src.tools.web_tools import get_tools
from src.tools.text_video import generate_video
from src.tools.text_speech import generate_speech


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
async def context_injection_node(state: State) -> dict:
    """Inject relevant context (e.g., activity, memory) into the state."""
    logger.system_info("Running context_injection_node")
    user_query = state["messages"][-1].content if state["messages"] else ""
    memory_context = state.get("memory_context", "")
    workflow = state.get("workflow", "conversation")

    # Use LLM to generate structured context for generation
    context_llm = get_llm_by_type("basic").with_structured_output(ContextForGeneration)
    context_prompt_vars = {
        "user_query": user_query,
        "memory_context": memory_context,
        "workflow": workflow
    }
    context_prompt = apply_prompt_template("context_injection_generation", context_prompt_vars)
    generated_context = await context_llm.invoke([HumanMessage(content=context_prompt)])
    
    return {"context_for_generation": generated_context.dict(), "current_activity": generated_context.general_instruction}

# --- Node: Conversation ---
def conversation_node(state: State, config: RunnableConfig) -> Command[Literal["summary"]]:
    """Handle conversation and generate AI response."""
    logger.system_info("Running conversation_node")
    user_query = state["messages"][-1].content

    # Assess complexity
    complexity_llm = get_llm_by_type("basic").with_structured_output(ComplexityAnalysis)
    complexity_prompt = apply_prompt_template("complexity_assessment", {"user_query": user_query})
    complexity_analysis = complexity_llm.invoke([HumanMessage(content=complexity_prompt)])

    if complexity_analysis.is_complex:
        logger.system_info(f"Complex query detected: {complexity_analysis.reason}. Using ReAct agent.")
        agent = create_agent("conversation_react", "tools", get_tools(), "CONVERSATION_PROMPT") # Assuming CONVERSATION_PROMPT can guide ReAct
        agent_response = agent.invoke(state["messages"])

        # Summarize agent's response
        summary_llm = get_llm_by_type("basic")
        summary_prompt = apply_prompt_template("agent_summary", {"agent_response": agent_response.content})
        summary_response = summary_llm.invoke([HumanMessage(content=summary_prompt)])
        response_content = summary_response.content
    else:
        logger.system_info("Simple query. Using basic LLM.")
        llm = get_llm_by_type("basic")
        prompt = apply_prompt_template("conversation", state["messages"])
        llm_response = llm.invoke([HumanMessage(content=prompt)])
        response_content = llm_response.content

    state["messages"].append(AIMessage(content=response_content))
    return Command(update={"messages": state["messages"]}, goto="summary")

# --- Node: Video ---
async def video_node(state: State, config: RunnableConfig) -> Command[Literal["summary"]]:
    """Handle video generation or processing."""
    logger.system_info("Running video_node")
    context_for_generation = state.get("context_for_generation")
    
    if not context_for_generation or not context_for_generation.get("video_prompt"):
        logger.warning("No video prompt in context for generation. Skipping video generation.")
        return Command(goto="summary")

    video_prompt = context_for_generation.get("video_prompt", "")
    negative_prompt = context_for_generation.get("negative_prompt", "")

    video_path = await generate_video(video_prompt, negative_prompt)
    
    return Command(update={"video_path": video_path}, goto="summary")

# --- Node: Audio ---
async def audio_node(state: State, config: RunnableConfig) -> Command[Literal["summary"]]:
    """Handle audio generation or processing."""
    logger.system_info("Running audio_node")
    context_for_generation = state.get("context_for_generation")
    
    if not context_for_generation or not context_for_generation.get("audio_dialogue"):
        logger.warning("No audio dialogue in context for generation. Skipping audio generation.")
        return Command(goto="summary")

    audio_dialogue = context_for_generation.get("audio_dialogue", "")

    audio_path = await generate_speech(audio_dialogue)
    
    return Command(update={"audio_path": audio_path}, goto="summary")

# --- Node: Summary ---
async def summary_node(state: State, config: RunnableConfig) -> Command[Literal["store_memory", "_end_"]]:
    """Summarize the conversation so far, including generated media if available."""
    logger.system_info("Running summary_node")
    
    video_path = state.get("video_path")
    audio_path = state.get("audio_path")
    summary_content = ""

    if video_path:
        summary_content = f"A video was generated and saved at: {video_path}."
    elif audio_path:
        summary_content = f"An audio snippet was generated and saved at: {audio_path}."
    else:
        # Original conversation summary logic
        agent = create_agent("summary", "basic", get_tools(), "SUMMARY_PROMPT")
        response = await agent.invoke(state["messages"])
        summary_content = response.content

    # Decide whether to store memory
    decision_llm = get_llm_by_type("basic").with_structured_output(MemoryStorageDecision)
    decision_prompt_vars = {"summary": summary_content}
    decision_prompt = apply_prompt_template("memory_storage_decision", decision_prompt_vars)
    storage_decision = await decision_llm.invoke([HumanMessage(content=decision_prompt)])

    if storage_decision.should_store:
        logger.info(f"Storing memory: {storage_decision.reason}")
        return Command(update={"summary": summary_content}, goto="store_memory")
    else:
        logger.info(f"Not storing memory: {storage_decision.reason}")
        return Command(goto="_end_")

# --- Node: Store Memory ---
async def store_memory_node(state: State) -> Command[Literal["router"]]:
    """Store the summary or important information in memory."""
    logger.system_info("Running store_memory_node")
    summary = state.get("summary", "")

    if summary:
        memory_manager = await get_memory_manager()
        await memory_manager.add_to_memory([{"role": "assistant", "content": summary}])
        logger.info(f"Stored summary: {summary}")
    else:
        logger.warning("No summary found to store in memory.")
        
    return Command(goto="router")
