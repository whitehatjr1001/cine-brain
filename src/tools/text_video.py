import asyncio
import logging
import os
import time
from typing import List, Optional

from src.config.execeptions import TextToVideoError
from src.prompts.prompts import get_prompt_template
from src.config.settings import settings
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class TextToVideo:
    """
    A comprehensive tool for an AI agent to plan and generate videos.

    This class provides a multi-step process for video creation:
    1.  plan_video_config: Dynamically determines the best technical video settings.
    2.  enhance_video_prompt: Creatively enhances the user's idea into a cinematic prompt.
    3.  generate_video: Executes the video generation with the planned config and prompt.
    """

    REQUIRED_ENV_VARS = ["GEMINI_API_KEY", "GROQ_API_KEY"]
    VEO_MODEL = "veo-2.0-generate-001"

    def __init__(self):
        """Initializes the TextToVideo tool and its logger."""
        self._validate_env_vars()
        self._genai_client: genai.Client | None = None
        self.logger = logging.getLogger(__name__)

    def _validate_env_vars(self) -> None:
        """Ensures all required API keys are set in the environment."""
        missing_vars = [var for var in self.REQUIRED_ENV_VARS if not os.getenv(var)]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    @property
    def genai_client(self) -> genai.Client:
        """Lazily initializes and returns the Google GenAI client."""
        if self._genai_client is None:
            self.logger.info("Initializing Google GenAI Client for Video Generation...")
            self._genai_client = genai.Client(
                http_options={"api_version": "v1beta"},
                api_key=settings.GEMINI_API_KEY,
            )
        return self._genai_client

    async def plan_video_config(self, user_prompt: str) -> VideoConfig:
        """
        Uses an LLM to analyze a user prompt and decide on the best video configuration.

        Args:
            user_prompt: The user's natural language request for a video.

        Returns:
            A Pydantic VideoConfig object with the optimal settings.
        """
        self.logger.info(f"Planning video configuration for prompt: '{user_prompt}'")
        try:
            llm = ChatGroq(
                model=settings.TEXT_MODEL_NAME,
                api_key=settings.GROQ_API_KEY,
                temperature=0.0,
            )
            structured_llm = llm.with_structured_output(VideoConfig)
            chain = PromptTemplate.from_template(VIDEO_CONFIG_PROMPT) | structured_llm

            video_config = await chain.ainvoke({"user_prompt": user_prompt})
            self.logger.info(f"Planned video configuration: {video_config.model_dump_json(indent=2)}")
            return video_config

        except Exception as e:
            self.logger.error(f"Failed to plan video config: {e}. Falling back to default.")
            return VideoConfig()

    async def enhance_video_prompt(self, prompt: str) -> str:
        """Enhances a simple prompt into a detailed cinematic prompt for VEO."""
        # This method is unchanged from our previous discussions.
        # It uses an LLM to make the creative prompt better.
        # Implementation details are in the prior responses.
        pass

    async def generate_video(
        self,
        prompt: str,
        config: VideoConfig,
        output_dir: str = "generated_videos",
    ) -> List[str]:
        """
        Asynchronously generates videos based on a prompt and a configuration object.

        Args:
            prompt: The final, enhanced cinematic prompt for the video.
            config: The Pydantic VideoConfig object with technical settings.
            output_dir: The directory where generated videos will be saved.

        Returns:
            A list of file paths to the generated videos.
        """
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        os.makedirs(output_dir, exist_ok=True)
        self.logger.info(f"Generating video with config: {config.model_dump()}")

        try:
            # Convert our Pydantic model to the google.genai specific type
            video_config_api = types.GenerateVideosConfig(
                person_generation="dont_allow",
                aspect_ratio=config.aspect_ratio,
                number_of_videos=config.number_of_videos,
                duration_seconds=config.duration_seconds,
                negative_prompt=config.negative_prompt,
            )

            operation = self.genai_client.models.generate_videos(
                model=self.VEO_MODEL,
                prompt=prompt,
                config=video_config_api,
            )

            self.logger.info(f"Video generation job started: {operation.name}")
            while not operation.done:
                self.logger.info("Generation in progress... checking again in 15s.")
                await asyncio.sleep(15)
                operation = self.genai_client.operations.get(operation.name)

            self.logger.info("Video generation job finished.")
            result = operation.result

            if not result or not result.generated_videos:
                raise TextToVideoError("The generation job completed but produced no videos.")

            saved_files = []
            for n, generated_video in enumerate(result.generated_videos):
                timestamp = int(time.time())
                file_path = os.path.join(output_dir, f"video_{timestamp}_{n}.mp4")
                generated_video.video.save(file_path)
                saved_files.append(file_path)
                self.logger.info(f"Video downloaded and saved to {file_path}")

            return saved_files

        except Exception as e:
            self.logger.error(f"An exception occurred during video generation: {e}")
            raise TextToVideoError(f"Failed to generate video: {e}") from e