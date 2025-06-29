from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template
from src.llm.llm import get_llm_by_type


# Create agents using configured LLM types
def create_agent(agent_name: str, agent_type: str, tools: list, prompt_template: str):
    """Factory function to create agents with consistent configuration."""
    return create_react_agent(
        name=agent_name,
        model=get_llm_by_type(agent_type),
        tools=tools,
        prompt=apply_prompt_template(prompt_template),
    )

