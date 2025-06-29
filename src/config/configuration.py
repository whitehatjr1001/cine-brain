import os
import yaml
from typing import Dict, Any, Literal
from pathlib import Path
from langchain_core.runnables import RunnableConfig

def get_config_path(relative_path: str = "agents_config.yaml") -> str:
    """Get absolute path to config file regardless of where code is run from."""
    # Get the directory where this settings.py file is located
    base_dir = Path(__file__).parent.absolute()
    return str(base_dir / relative_path)

# ------------- 1. LLM Type Definitions -------------

LLMType = Literal["basic", "tools", "prompt"]

# ------------- 2. Node to LLM Type Mapping -------------

# (Node-to-LLM mapping removed as it's no longer needed)

# ------------- 3. Config Loader (with env support) -------------

_config_cache: Dict[str, Dict[str, Any]] = {}

def _expand_env(value: str) -> str:
    """Replace $ENV_VAR with environment variable value."""
    if isinstance(value, str) and value.startswith("$"):
        env_var = value[1:]
        env_val = os.getenv(env_var)
        if env_val is None:
            raise ValueError(f"Environment variable '{env_var}' is not set")
        return env_val
    return value

def _process_dict(d: dict) -> dict:
    """Recursively expand env vars in all string values."""
    result = {}
    for k, v in d.items():
        if isinstance(v, dict):
            result[k] = _process_dict(v)
        elif isinstance(v, str):
            result[k] = _expand_env(v)
        else:
            result[k] = v
    return result

def load_yaml_config(file_path: str) -> Dict[str, Any]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file not found: {file_path}")
    if file_path in _config_cache:
        return _config_cache[file_path]
    with open(file_path, "r") as f:
        raw = yaml.safe_load(f)
    processed = _process_dict(raw)
    _config_cache[file_path] = processed
    return processed


# ------------- . Chat Agent Configuration -------------
import os
from dataclasses import dataclass, field, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig

@dataclass(kw_only=True)
class ChatAgentConfiguration:
    """
    Central configuration for incident chat agent workflow.
    """
    max_plan_iterations: int = 2  # e.g., retry planner at most twice
    max_step_num: int = 5         # e.g., at most 5 steps in a plan
    team_timeout: int = 60        # e.g., seconds to wait per team node
    enable_doc_steps: bool = True # optionally enable/disable documentation steps
    # Add more fields as needed!

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "ChatAgentConfiguration":
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        # Cast values to correct types
        for f in fields(cls):
            if f.name in values:
                if f.type is bool:
                    values[f.name] = str(values[f.name]).lower() == "true"
                elif f.type is int:
                    values[f.name] = int(values[f.name])
        return cls(**{k: v for k, v in values.items() if v is not None})


# ------------- Example Usage -------------
if __name__ == "__main__":
    os.environ["GROQ_API_KEY"] = "sk-xxxxxxx"  # for demo only, use env or .env in real cases
    llm = get_llm_for_agent("planner")
    print(llm.invoke("Hello, are you ready?"))

