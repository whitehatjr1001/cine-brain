from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig

from src.config.logger import logger
from src.config.settings import settings
from src.memory.memo_memory import add_to_memory, search_memory  # Updated import for memory tools
from src.prompts.prompts import apply_prompt_template
from src.llm.llm import get_llm_by_type
from src.graph.state import CineBrainState as State


class MemoryAnalysis(BaseModel):
    """Structured result from LLM determining if memory is important."""
    is_important: bool = Field(..., description="Should this be stored in long-term memory?")
    formatted_memory: Optional[str] = Field(None, description="Formatted memory to store")


class MemoryManager:
    """
    Memory manager that uses an LLM and Mem0 tools to store/retrieve long-term memory.
    Compatible with the updated codebase and synchronous memory tools.
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.llm = get_llm_by_type("basic").with_structured_output(MemoryAnalysis)

    def _state_to_dict(self, state) -> dict:
        if hasattr(state, 'dict'):
            state_dict = state.dict()
        elif isinstance(state, dict):
            state_dict = state
        else:
            state_dict = vars(state)
        # Ensure messages are serializable (list of dicts or strings)
        if "messages" in state_dict:
            state_dict["messages"] = [
                m.dict() if hasattr(m, "dict") else (vars(m) if hasattr(m, "__dict__") else str(m))
                for m in state_dict["messages"]
            ]
        return state_dict

    def analyze_memory(self, user_query: str) -> MemoryAnalysis:
        """Use the LLM to analyze whether a message is important and how to store it."""
        prompt = apply_prompt_template("memory_extraction", {"user_query": user_query})
        return self.llm.invoke(prompt)

    def extract_and_store_memories(self, last_message) -> None:
        if getattr(last_message, "type", None) != "human":
            return
        analysis = self.analyze_memory(last_message.content)
        if not (analysis and analysis.is_important and analysis.formatted_memory):
            return
        config = RunnableConfig(configurable={"user_id": self.user_id})
        existing = search_memory.invoke({"query": analysis.formatted_memory}, config=config)
        if analysis.formatted_memory in existing:
            logger.warning(f"Duplicate memory found. Skipping: '{analysis.formatted_memory}'")
            return
        logger.system_info(f"Storing memory: '{analysis.formatted_memory}'")
        add_to_memory.invoke({"content": analysis.formatted_memory}, config=config)

    def retrieve_memories(self, query: str) -> List[str]:
        """Search for relevant memories using Mem0."""
        config = RunnableConfig(configurable={"user_id": self.user_id})
        raw_results = search_memory(query, config=config)
        if not raw_results:
            return []
        return [line.strip("- ").strip() for line in raw_results.split("\n") if line.strip()]

    def format_memories_for_prompt(self, memories: List[str]) -> str:
        """Format a list of memories as bullet points for prompt injection."""
        if not memories:
            return ""
        return "\n".join(f"- {mem}" for mem in memories)
