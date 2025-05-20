import os
from typing import Optional

from src.config.execeptions import TextToSpeechError
from src.config.settings import settings
from groq import Groq
from groq import Audio

class TextToSpeech:
    """A class to handle text-to-speech conversion using ElevenLabs."""

    # Required environment variables
    REQUIRED_ENV_VARS = ["GROQ_API_KEY", "TTS_MODEL_NAME", "TTS_VOICE"]

    def __init__(self):
        """Initialize the TextToSpeech class and validate environment variables."""
        self._validate_env_vars()
        self._client: Optional[Groq] = None

    def _validate_env_vars(self) -> None:
        """Validate that all required environment variables are set."""
        missing_vars = [var for var in self.REQUIRED_ENV_VARS if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    @property
    def client(self):
        """Get or create ElevenLabs client instance using singleton pattern."""
        if self._client is None:
            self._client = Groq(api_key=settings.GROQ_API_KEY)
        return self._client

    async def synthesize(self, text: str) -> bytes:
        """Convert text to speech using ElevenLabs.

        Args:
            text: Text to convert to speech

        Returns:
            bytes: Audio data

        Raises:
            ValueError: If the input text is empty or too long
            TextToSpeechError: If the text-to-speech conversion fails
        """
        if not text.strip():
            raise ValueError("Input text cannot be empty")

        if len(text) > 5000:  # ElevenLabs typical limit
            raise ValueError("Input text exceeds maximum length of 5000 characters")

        try:
            audio_generator = self.client.audio.speech.create(
                model=settings.TTS_MODEL_NAME,
                voice=settings.TTS_VOICE,
                response_format="wav",
                input=text,
            )

            # Convert generator to bytes
            audio_bytes = await audio_generator.content()
            if not audio_bytes:
                raise TextToSpeechError("Generated audio is empty")

            return audio_bytes

        except Exception as e:
            raise TextToSpeechError(f"Text-to-speech conversion failed: {str(e)}") from e

text_to_speech = TextToSpeech()
