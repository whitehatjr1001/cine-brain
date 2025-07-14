from .imdb_api import imdb_api
from .box_office_predictor import box_office_predictor
from .web_serch import web_search

def get_tools():
    tools = [imdb_api,box_office_predictor,web_search]
    return tools
