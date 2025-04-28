from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from src.config.settings import settings
import re

def get_llm(temperature: float = 0.7):
    return ChatGroq(
        api_key=settings.GROK_API_KEY,
        temperature=temperature,
        model_name = settings.MODEL_NAME
    )
    
de get_tts_llm(temperature: float = 0.7):
    return ChatGroq(
        api_key=settings.GROK_API_KEY,
        temperature=temperature,
        model_name = settings.MODEL_NAME
    )

def get_text_image_llm(temperature: float = 0.7):
    return ChatGroq(
        api_key=settings.GROK_API_KEY,
        temperature=temperature,
        model_name = settings.MODEL_NAME
    )
def remove_asterisk_content(text: str) -> str:
    """Remove content between asterisks from the text."""
    return re.sub(r"\*.*?\*", "", text).strip()


class CleanOutput(StrOutputParser):
    def parse(self, text: str) -> str:
        return remove_asterisk_content(super().parse(text))
    

    