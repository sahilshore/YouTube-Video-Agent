"""Groq OpenAI-compatible provider."""

from src.providers.openai_compatible import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        super().__init__(api_key=api_key, base_url=base_url, model=model, name="groq")

