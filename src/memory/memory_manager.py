from src.config.logger import logger
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langchain_core.tools import Tool
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq

from src.config.settings import settings
from src.memory.tools import add_to_memory, search_memory  # Assuming tools are defined already
from src.memory.prompt_templates import MEMORY_ANALYSIS_PROMPT  # Your prompt format for LLM



class MemoryAnalysis(BaseModel):
    """Structured result from LLM determining if memory is important."""
    is_important: bool = Field(..., description="Should this be stored in long-term memory?")
    formatted_memory: Optional[str] = Field(None, description="Formatted memory to store")


class MemoryManager:
    """Memory manager that uses an LLM and Mem0 tools to store/retrieve long-term memory."""

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.llm: Runnable = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.SMALL_TEXT_MODEL_NAME,
            temperature=0.1,
        ).with_structured_output(MemoryAnalysis)

    async def _analyze_memory(self, message: str) -> MemoryAnalysis:
        """Use the LLM to analyze whether a message is important and how to store it."""
        prompt = MEMORY_ANALYSIS_PROMPT.format(message=message)
        return await self.llm.ainvoke(prompt)

    async def extract_and_store_memories(self, message: BaseMessage) -> None:
        """Extract and store memory if it's deemed important by the LLM."""
        if message.type != "human":
            return

        analysis = await self._analyze_memory(message.content)
        if analysis.is_important and analysis.formatted_memory:
            # Search for similar memory
            context_wrapper = {"context": {"user_id": self.user_id}}
            existing = await search_memory.invoke(
                query=analysis.formatted_memory,
                context=context_wrapper
            )

            if analysis.formatted_memory in existing:
                logger.info(f"Memory already exists: '{analysis.formatted_memory}'")
                return

            # Add new memory
            logger.info(f"Storing memory: '{analysis.formatted_memory}'")
            await add_to_memory.invoke(
                content=analysis.formatted_memory,
                context=context_wrapper
            )

    async def retrieve_memories(self, query: str) -> List[str]:
        """Search for relevant memories using Mem0."""
        context_wrapper = {"context": {"user_id": self.user_id}}
        raw_results = await search_memory.invoke(query=query, context=context_wrapper)
        return raw_results.split("\n") if raw_results else []

    def format_memories_for_prompt(self, memories: List[str]) -> str:
        """Format a list of memories as bullet points for prompt injection."""
        if not memories:
            return ""
        return "\n".join(f"- {mem}" for mem in memories)
