from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from dotenv import load_dotenv
import os

# Find project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

# Load the .env manually early
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    raise FileNotFoundError(f".env file not found at {ENV_FILE}")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    GROK_API_KEY: str
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    TTS_MODEL_NAME: str = "playai-tts"
    MEMO_API_KEY: str
    SERPER_API_KEY: str
    GEMINI_API_KEY: str
    


settings = Settings()
