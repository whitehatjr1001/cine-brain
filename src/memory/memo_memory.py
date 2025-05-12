from __future__ import annotations
import os
import asyncio
from pydantic import BaseModel
from src.config.settings import settings
try:
    from mem0 import AsyncMemoryClient
except ImportError:
    raise ImportError("mem0 is not installed. Please install it using 'pip install mem0ai'.")
from langraph.tools import tool

class Mem0Context(BaseModel):
    user_id: str | None = None

client = AsyncMemoryClient(api_key=settings.MEMO_API_KEY)

class RunContextWrapper:
    def __init__(self, context):
        self.context = context

@tool
async def add_to_memory(context: RunContextWrapper[Mem0Context], content: str) -> str:
    """
    Add a message to Mem0
    Args:
        content: The content to store in memory.
    """
    messages = [{"role": "user", "content": content}]
    user_id = context.context.user_id or "default_user"
    await client.add(messages, user_id=user_id)
    return f"Stored message: {content}"

@tool
async def search_memory(context: RunContextWrapper[Mem0Context], query: str) -> str:
    """
    Search for memories in Mem0
    Args:
        query: The search query.
    """
    user_id = context.context.user_id or "default_user"
    memories = await client.search(query, user_id=user_id, output_format="v1.1")
    results = '\n'.join([result["memory"] for result in memories["results"]])
    return str(results)

@tool
async def get_all_memory(context: RunContextWrapper[Mem0Context]) -> str:
    """Retrieve all memories from Mem0"""
    user_id = context.context.user_id or "default_user"
    memories = await client.get_all(user_id=user_id, output_format="v1.1")
    results = '\n'.join([result["memory"] for result in memories["results"]])
    return str(results)

# Example agent configuration and runtime loop are omitted here; integrate with your agent framework as needed.
# This module now provides async memory tools for agentic use with Mem0.
        