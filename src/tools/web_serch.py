from crawl4ai import AsyncCrawler
import requests
from src.config import settings
from src.config.logger import logger

def web_research(query: str) -> str:
    """Search the web for information."""
    try:
        api_key = settings.SERPER_API_KEY
        base_url = "https://google.serper.dev/search"
        payload = {
            "q": query,
            "api_key": api_key
        }
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", base_url, headers=headers, data=payload)
        return response.json()
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return "Web search failed."

from langchain_core.tools import tool
@tool
async def web_search(query: str,num_results: int = 5) -> str:
    """Search the web for information."""
    try:
        urls = web_research(query)
        crawler = AsyncCrawler()
        results = []
        for i in range(num_results):
            response = await crawler.get(urls["organic_results"][i]["link"])
            results.append(response.markdown)
        return "\n".join(results)
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return "Web search failed."

