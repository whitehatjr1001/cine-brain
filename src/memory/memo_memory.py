from __future__ import annotations
import asyncio
from pydantic import BaseModel
from src.config.settings import settings
from src.config.logger import logger


# Mem0 client
from mem0 import AsyncMemoryClient

# LangGraph tool decorator & config
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

client = AsyncMemoryClient(api_key=settings.MEMO_API_KEY)

class Mem0Config(BaseModel):
    """Schema for configurable runtime data."""
    user_id: str | None = None

async def add_to_memory(messages: list[dict], user_id: str) -> str:
    """
    Add a list of messages to the memory.   
    """
    await client.add(messages, user_id=user_id)
    return f"✅ Stored messages for {user_id}"

async def search_memory(query: str, user_id: str) -> list[str]:
    filters = {
   "AND": [
      {
         "user_id": user_id
      }
   ]
}

    all_memories = client.get_all(version="v2", filters=filters, page=1, page_size=50)
    return all_memories
