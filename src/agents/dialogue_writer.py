# dialogue_writer.py
from langgraph.prebuilt import create_react_agent

class DialogueWriter:
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.agent = create_react_agent("dialogue_writer")

    async def write_dialogue(self, message: BaseMessage) -> str:
        """Write a dialogue based on the given message."""
        return await self.agent.invoke(message.content)
    
agent = DialogueWriter()
