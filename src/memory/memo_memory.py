from __future__ import annotations
import asyncio
from pydantic import BaseModel
from src.config.settings import settings

# Mem0 client
from mem0 import AsyncMemoryClient

# LangGraph tool decorator & config
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

client = AsyncMemoryClient(api_key=settings.MEMO_API_KEY)

class Mem0Config(BaseModel):
    """Schema for configurable runtime data."""
    user_id: str | None = None

@tool
async def add_to_memory(
    content: str,
    config: RunnableConfig
) -> str:
    """
    Store a piece of content in Mem0 under the given user_id.
    """
    user_id = config["configurable"].get("user_id") or "default_user"
    messages = [{"role": "user", "content": content}]
    await client.add(messages, user_id=user_id)
    return f"✅ Stored message for {user_id}: “{content}”"

@tool
async def search_memory(
    query: str,
    config: RunnableConfig
) -> str:
    """
    Search Mem0 for memories matching the query.
    """
    user_id = config["configurable"].get("user_id") or "default_user"
    memories = await client.search(query, user_id=user_id, output_format="v1.1")
    results = [item["memory"] for item in memories.get("results", [])]
    if not results:
        return "No matching memories found."
    return "\n".join(f"- {m}" for m in results)

@tool
async def get_all_memory(
    config: RunnableConfig
) -> str:
    """
    Retrieve all stored memories for the current user.
    """
    user_id = config["configurable"].get("user_id") or "default_user"
    memories = await client.get_all(user_id=user_id, output_format="v1.1")
    results = [item["memory"] for item in memories.get("results", [])]
    if not results:
        return "No memories stored yet."
    return "\n".join(f"- {m}" for m in results)

meory_manager_tools = ["add_to_memory", "search_memory", "get_all_memory"]