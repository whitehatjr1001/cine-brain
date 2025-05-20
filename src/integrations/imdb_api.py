# imdb_api.py
from bs4 import BeautifulSoup
import requests
import re
from src.config import settings
from langchain_core.tools import tool
    
class IMDbAPI:
    def __init__(self):
        self.api_key = settings.SERPER_API_KEY
        self.base_url = "https://google.serper.dev/search"
        
    @tool
    async def search(self, query: str) -> str:
        payload = {
            "q": query,
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
        urls =  await self.search(query)
        for url in urls["organic_results"]:
            response = requests.get(url["link"])
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            return text
        
    @tool
    async def get_movie_info(self, query: str) -> str:
        urls =  await self.search(query)
        for url in urls["organic_results"]:
            response = requests.get(url["link"])
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            return text
        