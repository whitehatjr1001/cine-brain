from langchain_comunity import chains 
from .prompts import *

def get_llm_chain(llm):
    return chains.LLMChain(llm=llm, prompt=ROUTING_PROMPT)

def get_tts_chain(llm):
    return chains.LLMChain(llm=llm, prompt=TTS_PROMPT)

def get_text_to_image_chain(llm):
    return chains.LLMChain(llm=llm, prompt=TEXT_TO_IMAGE_PROMPT)

