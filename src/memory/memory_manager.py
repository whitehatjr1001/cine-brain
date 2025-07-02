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
    Memory manager for extracting and (optionally) storing long-term memory.
    Now split into extract_memory (for context) and store_memory (for persistence).
    """
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.llm = get_llm_by_type("basic").with_structured_output(MemoryAnalysis)

    def analyze_memory(self, user_query: str) -> MemoryAnalysis:
        prompt = apply_prompt_template("memory_extraction", {"user_query": user_query})
        return self.llm.invoke(prompt)

    async def extract_memory(self, user_query: str) -> str:
        """
        Analyze the user query. If important, search for relevant memory and return it as context.
        If not important or not found, return an empty string.
        """
        analysis = self.analyze_memory(user_query)
        if not (analysis and analysis.is_important and analysis.formatted_memory):
            return ""
        if analysis.formatted_memory:
            memories = await search_memory(analysis.formatted_memory, self.user_id)
            
        return memories
    
    async def store_memory(self, memories: str) -> None:
        """
        Store the memory if it's important and not already present.
        """
        add_to_memory(memories, self.user_id)
        return f" Stored memory for {self.user_id}"
    
    def format_memories_for_prompt(self, memories: list[dict]) -> str:
        memory_context = ""
        for memory in memories:
            memory_context += memory
        return memory_context
