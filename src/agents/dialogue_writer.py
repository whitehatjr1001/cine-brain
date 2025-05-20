from langgraph.agents import Agent
from src.prompts.prompts import DIALOGUE_WRITER_PROMPT
from src.config.settings import settings
from src.utils.helpers import get_llm

class DialogueWriter:
    def __init__(self):
        self.agent = Agent(prompt=DIALOGUE_WRITER_PROMPT, llm=get_llm(settings.LLM_MODEL))

    def write_dialogue(self, message: str) -> str:
        return self.agent.invoke(message)

dialogue_writer = DialogueWriter()

if __name__ == "__main__":
    dialogue_writer.write_dialogue("This is a message.")


