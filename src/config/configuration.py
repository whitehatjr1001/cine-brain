from typing import Literal

# Define available LLM types
LLMType = Literal["basic", "reasoning", "vision"]

# Define agent-LLM mapping
AGENT_LLM_MAP: dict[str, LLMType] = {
    "coordinator": "basic",
    "planner": "basic",
    "research_team": "basic",
    "writing_team": "basic",
    "script_writer": "basic",
    
}

