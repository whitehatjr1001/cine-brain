from __future__ import annotations
import asyncio
from pydantic import BaseModel
from src.config.settings import settings
from src.config.logger import logger

# Mem0 client
from mem0 import AsyncMemoryClient



client = AsyncMemoryClient(api_key=settings.MEMO_API_KEY)



async def add_to_memory(messages: list[dict], user_id: str) -> str:
    """
    Add a list of messages to the memory.   
    """
    logger.system_info(f"Adding messages to Mem0: {messages}")  # Debug print
    await client.add(messages, user_id=user_id, output_format='v1.1')
    return f"Stored messages for {user_id}"

async def search_memory(query: str, user_id: str) -> list[str]:
    filters = {
   "AND": [
      {
         "user_id": user_id
      }
   ]
}

    all_memories = await client.get_all(version="v2", filters=filters, page=1, page_size=50)
    return all_memories
