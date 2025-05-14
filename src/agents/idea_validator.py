# idea_validator.py
from langraph.prebuilt import create_react_agent

class IdeaValidator:
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.agent = create_react_agent("idea_validator")

    async def validate_idea(self, idea: str) -> bool:
        """Validate whether the given idea is valid or not."""
        return await self.agent.invoke(idea)
idea_validator = IdeaValidator()
