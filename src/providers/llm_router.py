"""Provider selection and safe fallback routing."""

from __future__ import annotations

from collections.abc import Callable

from config.settings import Settings
from src.core.exceptions import ConfigurationError, ProviderError
from src.providers.base import LLMProvider
from src.providers.gemini_provider import GeminiProvider
from src.providers.groq_provider import GroqProvider
from src.providers.ollama_provider import OllamaProvider
from src.providers.openrouter_provider import OpenRouterProvider


class LLMRouter:
    def __init__(self, settings: Settings, factories: dict[str, Callable[[], LLMProvider]] | None = None) -> None:
        self.settings = settings
        self._factories = factories or self._default_factories()
        self._providers: dict[str, LLMProvider] = {}

    def _default_factories(self) -> dict[str, Callable[[], LLMProvider]]:
        s = self.settings
        return {
            "gemini": lambda: GeminiProvider(s.gemini_api_key, s.gemini_model),
            "groq": lambda: GroqProvider(s.groq_api_key, s.groq_base_url, s.groq_model),
            "openrouter": lambda: OpenRouterProvider(s.openrouter_api_key, s.openrouter_base_url, s.openrouter_model, s.free_only_mode),
            "ollama": lambda: OllamaProvider(s.ollama_base_url, s.ollama_model, s.ollama_timeout),
        }

    def get(self, name: str | None = None) -> LLMProvider:
        provider_name = (name or self.settings.default_llm_provider).lower()
        if provider_name not in self._factories:
            raise ConfigurationError(f"Unknown LLM provider: {provider_name}")
        if provider_name not in self._providers:
            self._providers[provider_name] = self._factories[provider_name]()
        return self._providers[provider_name]

    def generate_text(self, prompt: str, provider: str | None = None, fallback: list[str] | None = None) -> str:
        names = [provider or self.settings.default_llm_provider, *(fallback or [])]
        errors: list[str] = []
        for name in dict.fromkeys(names):
            try:
                return self.get(name).generate_text(prompt)
            except Exception as exc:
                errors.append(f"{name}: {exc}")
        raise ProviderError("All configured LLM providers failed: " + " | ".join(errors))

    def connection_status(self) -> dict[str, tuple[bool, str]]:
        status: dict[str, tuple[bool, str]] = {}
        for name in self._factories:
            try:
                status[name] = self.get(name).test_connection()
            except Exception as exc:
                status[name] = (False, str(exc))
        return status

