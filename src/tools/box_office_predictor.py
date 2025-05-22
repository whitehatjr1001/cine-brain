# trope_detector.py
from langchain_core.tools import tool
from src.config import settings
from src.utils.helpers import get_llm
from langgraph.agents import Agent
from src.prompts.prompts import TROPE_DETECTOR_PROMPT
from crawl4ai import AsyncCrawler
import requests
from src.config.logger import logger

class BoxOfficePredictor:
    def __init__(self, query: str):
        self.SERPER_API_KEY = settings.SERPER_API_KEY
        self.base_url = "https://google.serper.dev/search"
        self.payload = {
            "q": "site:the-numbers.com " + query,
            "api_key": self.SERPER_API_KEY
        }
        self.headers = {
            'X-API-KEY': self.SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
    async def predict(self):
        logger.info(f"Predicting box office for {self.payload}")
        response = requests.request("POST", self.base_url, headers=self.headers, data=self.payload)
        return response.json()
    
    @tool
    async def get_movie_info(self) -> str:
        urls =  await self.predict()
        for url in urls["organic_results"]:
            response = await AsyncCrawler().get(url["link"])
            return response.markdown
        
    tools = [
        get_movie_info,
    ]

box_office_predictor = BoxOfficePredictor(query="Avatar")
