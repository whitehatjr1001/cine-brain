from pathlib import Path
from typing import Any, Dict
import os

from langchain_groq import ChatGroq

from src.config.configuration import load_yaml_config, LLMType

# Cache for LLM instances
_llm_cache: dict[LLMType, ChatGroq] = {}


def _get_env_llm_conf(llm_type: str) -> Dict[str, Any]:
    """
    Get LLM configuration from environment variables.
    Environment variables should follow the format: {LLM_TYPE}__{KEY}
    e.g., BASIC_MODEL__api_key, BASIC_MODEL__base_url
    """
    prefix = f"{llm_type.upper()}_MODEL__"
    conf = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            conf_key = key[len(prefix) :].lower()
            conf[conf_key] = value
    return conf


def _create_llm_use_conf(llm_type: LLMType, conf: Dict[str, Any]) -> ChatGroq:
    llm_type_map = {
        "tools": conf.get("TOOLS_MODEL", {}),
        "basic": conf.get("BASIC_MODEL", {}),
        "prompt": conf.get("PROMPT_MODEL", {}),
    }
    llm_conf = llm_type_map.get(llm_type)
    if not isinstance(llm_conf, dict):
        raise ValueError(f"Invalid LLM Conf: {llm_type}")
    # Get configuration from environment variables
    env_conf = _get_env_llm_conf(llm_type)

    # Merge configurations, with environment variables taking precedence
    merged_conf = {**llm_conf, **env_conf}

    if not merged_conf:
        raise ValueError(f"Unknown LLM Conf: {llm_type}")

    return ChatGroq(**merged_conf)


def get_llm_by_type(
    llm_type: LLMType,
) -> ChatGroq:
    """
    Get LLM instance by type. Returns cached instance if available.
    """
    if llm_type in _llm_cache:
        return _llm_cache[llm_type]

    config_path = Path(__file__).parent.parent / "config" / "agents_config.yaml"
    conf = load_yaml_config(str(config_path.resolve()))
    llm = _create_llm_use_conf(llm_type, conf)
    _llm_cache[llm_type] = llm
    return llm


if __name__ == "__main__":
    # Initialize LLMs for different purposes - now these will be cached
    basic_llm = get_llm_by_type("basic")
    print(basic_llm.invoke("Hello"))
