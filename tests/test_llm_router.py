from dataclasses import replace

import pytest
import requests

from config.settings import Settings
from src.core.exceptions import ConfigurationError, ProviderError
from src.providers.base import LLMProvider
from src.providers.llm_router import LLMRouter
from src.providers.openrouter_provider import OpenRouterProvider
from src.providers.ollama_provider import OllamaProvider


class FakeProvider(LLMProvider):
    def __init__(self, name: str, response: str | None = None, error: Exception | None = None) -> None:
        self.name = name
        self.model = "fake"
        self.response = response
        self.error = error

    def generate_text(self, prompt: str, *, temperature: float = 0.7) -> str:
        if self.error:
            raise self.error
        return self.response or "ok"

    def test_connection(self) -> tuple[bool, str]:
        return True, "ok"


def test_router_falls_back_to_next_provider() -> None:
    settings = replace(Settings(), default_llm_provider="first")
    router = LLMRouter(settings, {"first": lambda: FakeProvider("first", error=RuntimeError("down")), "second": lambda: FakeProvider("second", response="fallback")})
    assert router.generate_text("hello", fallback=["second"]) == "fallback"


def test_router_reports_all_failures() -> None:
    router = LLMRouter(Settings(default_llm_provider="first"), {"first": lambda: FakeProvider("first", error=RuntimeError("down"))})
    with pytest.raises(ProviderError, match="All configured"):
        router.generate_text("hello")


def test_openrouter_blocks_paid_model_in_free_mode() -> None:
    with pytest.raises(ConfigurationError):
        OpenRouterProvider("key", "https://example.com", "some/model", free_only=True)


def test_ollama_timeout_error_is_actionable(monkeypatch) -> None:
    def timeout(*args, **kwargs):
        raise requests.ReadTimeout("slow local generation")

    monkeypatch.setattr("src.providers.ollama_provider.requests.post", timeout)
    with pytest.raises(ProviderError, match="OLLAMA_TIMEOUT"):
        OllamaProvider(timeout=5).generate_text("hello")

