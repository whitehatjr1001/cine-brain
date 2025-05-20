# vibe_matcher.py
from langgraph.agents import Agent
from src.prompts.prompts import VIBE_MATCH_PROMPT
from src.config.settings import settings
from src.utils.helpers import get_llm
class VibeMatcher:
    def __init__(self):
        self.agent = Agent(prompt=VIBE_MATCH_PROMPT, llm=get_llm(settings.LLM_MODEL))

    def match_vibe(self, text: str) -> bool:
        return self.agent.invoke(text)

vibe_matcher = VibeMatcher()

if __name__ == "__main__":
    vibe_matcher.match_vibe("This is a text.")
