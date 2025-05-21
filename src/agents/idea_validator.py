# idea_validator.py
from langraph.prebuilt import create_react_agent
from src.config.settings import settings
from src.utils.helpers import get_llm
from src.prompts.prompts import IDEA_VALIDATOR_PROMPT
from langchain_core.tools import tool
from src.integrations.box_office_predictor import box_office_predictor

class IdeaValidator:
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.agent = create_react_agent("idea_validator", llm=get_llm(settings.LLM_MODEL), prompt=IDEA_VALIDATOR_PROMPT, tools=[
            tool(lambda x: x),
            box_office_predictor.get_movie_info
        ])

    async def validate_idea(self, idea: str) -> bool:
        """Validate whether the given idea is valid or not."""
        return await self.agent.invoke(idea, config={"configurable": {"user_id": self.user_id}})
idea_validator = IdeaValidator()
