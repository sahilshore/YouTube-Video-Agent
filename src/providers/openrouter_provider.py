"""OpenRouter provider with an explicit free-model guard."""

from src.core.exceptions import ConfigurationError
from src.providers.openai_compatible import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    def __init__(self, api_key: str, base_url: str, model: str, free_only: bool = True) -> None:
        if free_only and not (model == "openrouter/free" or model.endswith(":free") or ":free" in model):
            raise ConfigurationError("FREE_ONLY_MODE blocks non-free OpenRouter model IDs")
        super().__init__(api_key=api_key, base_url=base_url, model=model, name="openrouter")

