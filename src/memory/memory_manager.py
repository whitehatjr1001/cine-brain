from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_groq import ChatGroq

from src.config.logger import logger
from src.config.settings import settings
from src.memory.tools import add_to_memory, search_memory  # Tools must be LangChain @tool
from src.memory.prompt_templates import MEMORY_ANALYSIS_PROMPT  # Your structured prompt


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
        if not (analysis and analysis.is_important and analysis.formatted_memory):
            return

        # Config object for tool execution
        config = RunnableConfig(configurable={"user_id": self.user_id})

        # Check for existing memory
        existing = await search_memory.ainvoke(
            {"query": analysis.formatted_memory},
            config=config
        )

        if analysis.formatted_memory in existing:
            logger.warning(f"Duplicate memory found. Skipping: '{analysis.formatted_memory}'")
            return

        # Store memory
        logger.info(f"Storing memory: '{analysis.formatted_memory}'")
        await add_to_memory.ainvoke(
            {"content": analysis.formatted_memory},
            config=config
        )

    async def retrieve_memories(self, query: str) -> List[str]:
        """Search for relevant memories using Mem0."""
        config = RunnableConfig(configurable={"user_id": self.user_id})

        raw_results = await search_memory.ainvoke(
            {"query": query},
            config=config
        )

        if not raw_results:
            return []

        return [line.strip("- ").strip() for line in raw_results.split("\n") if line.strip()]

    def format_memories_for_prompt(self, memories: List[str]) -> str:
        """Format a list of memories as bullet points for prompt injection."""
        if not memories:
            return ""
        return "\n".join(f"- {mem}" for mem in memories)
