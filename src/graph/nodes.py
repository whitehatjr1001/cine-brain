from src.graph.state import CineBrainState
from src.prompts.prompts import apply_prompt_template
from src.prompts.planner_module import PlannerResponse,MemoryAnalysis
from src.llm.llm import get_llm_by_type
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.runnables import RunnableConfig
from src.config.settings import settings
from langgraph.graph import Command 


def memmory_extraction_node(state: CineBrainState) -> Command:
    llm = get_llm_by_type("basic")
    
    prompt = apply_prompt_template(state.messages)
    messages = state.messages[:-1]
    messages.append(HumanMessage(content=prompt))
    response = llm.with_structured_output(MemoryAnalysis).invoke(messages)
    state.messages.append(AIMessage(content=response))
    if response.is_important and response.formatted_memory:
        memory_manager = MemoryManager(user_id=settings.USER_ID)
        memories = memory_manager.extract_and_store_memories(response.formatted_memory)
        state.memory_context.append(memories)
    
    return Command(state)

def planner_node(state: CineBrainState) -> Command:
    llm = get_llm_by_type("basic")
    
    prompt = apply_prompt_template(state.messages)
    messages = state.messages[:-1]
    messages.append(HumanMessage(content=prompt))
    response = llm.with_structured_output(PlannerResponse).invoke(messages)
    state.messages.append(AIMessage(content=response))
    if response.has_enough_context:
        state.plan = response.steps
    else:
        state.plan = []    
    return Command(state)

        
def conversation_node(state: CineBrainState) -> Command:
    llm = get_llm_by_type("basic")
    
    prompt = apply_prompt_template(state.messages)
    messages = state.messages[:-1]
    messages.append(HumanMessage(content=prompt))
    response = llm.invoke(messages)
    state.messages.append(AIMessage(content=response))
    return Command(state)

def audio_node(state: CineBrainState) -> Command:
    llm = get_llm_by_type("basic")
    
    prompt = apply_prompt_template(state.messages)
    messages = state.messages[:-1]
    messages.append(HumanMessage(content=prompt))
    response = llm.invoke(messages)
    state.messages.append(AIMessage(content=response))
    return Command(state)

def video_node(state: CineBrainState) -> Command:
    llm = get_llm_by_type("basic")
    
    prompt = apply_prompt_template(state.messages)
    messages = state.messages[:-1]
    messages.append(HumanMessage(content=prompt))
    response = llm.invoke(messages)
    state.messages.append(AIMessage(content=response))
    return Command(state)

