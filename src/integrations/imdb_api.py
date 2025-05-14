# imdb_api.py
from bs4 import BeautifulSoup
import requests
import re
from src.config import settings
from langchain_core.tools import tool


class IMDBAPI:
    def __init__(self):
        