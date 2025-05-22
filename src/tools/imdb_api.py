import requests
import re
from src.config import settings
from langchain_core.tools import tool
from crawl4ai import AsyncCrawler
from src.config.logger import logger

class IMDbAPI:
    def __init__(self):
        self.api_key = settings.SERPER_API_KEY
        self.base_url = "https://google.serper.dev/search"
        
    
    async def search(self, query: str) -> str:
        logger.info(f"Searching for {query}")
        payload = {
            "q": "site:imdb.com " + query,
            "api_key": self.api_key
        }
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", self.base_url, headers=headers, data=payload)
        return response.json()
    
    @tool
    async def get_movie_info(self, query: str) -> str:
        logger.info(f"Getting movie info for {query}")
        urls =  await self.search(query)
        crawler = AsyncCrawler()
        for url in urls["organic_results"]:
            response = await crawler.get(url["link"])
            return response.markdown
        
    tools = [   
        get_movie_info,
    ]

imbdapi = IMDbAPI()
