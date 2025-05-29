import requests
import re
from src.config import settings
from langchain_core.tools import tool
from crawl4ai import AsyncCrawler
from src.config.logger import logger

@tool
def imdb_api(query: str,num_results: int = 5) -> str:
    api_key = settings.SERPER_API_KEY
    base_url = "https://google.serper.dev/search"
    payload = {
        "q": "site:imdb.com " + query,
        "api_key": api_key
    }
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", base_url, headers=headers, data=payload)
    logger.info(f"Serching the web for: {query}")
    urls = response.json()
    
    crawler = AsyncCrawler()
    results = []
    for url in urls["organic_results"][:num_results]:
        response = crawler.get(url["link"])
        results.append(response.markdown)
    
    return "\n".join(results)
    
