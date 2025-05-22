from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template
from src.utils.helpers import get_llm
from src.config.settings import settings


# Create agents using configured LLM types
def create_agent(agent_name: str, agent_type: str, tools: list, prompt_template: str):
    """Factory function to create agents with consistent configuration."""
    return create_react_agent(
        name=agent_name,
        model=get_llm(settings.AGENT_LLM_MAP[agent_type]),
        tools=tools,
        prompt=apply_prompt_template(prompt_template),
    )

