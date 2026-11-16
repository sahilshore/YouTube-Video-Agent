"""Shared implementation for OpenAI-compatible hosted providers."""

from __future__ import annotations

from src.core.exceptions import ProviderError
from src.providers.base import LLMProvider, provider_error
from src.utils.retry_utils import retry


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, *, api_key: str, base_url: str, model: str, name: str) -> None:
        self.require_key(api_key, name)
        self.name = name.lower()
        self.model = model
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate_text(self, prompt: str, *, temperature: float = 0.7) -> str:
        try:
            response = retry(lambda: self.client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}], temperature=temperature), attempts=3)
            text = response.choices[0].message.content if response.choices else ""
            if not text:
                raise ProviderError(f"{self.name} returned an empty response")
            return text
        except ProviderError:
            raise
        except Exception as exc:
            raise provider_error(self.name.title(), exc) from exc

    def test_connection(self) -> tuple[bool, str]:
        try:
            self.generate_text("Reply with the single word OK.", temperature=0)
            return True, f"{self.name.title()} {self.model} is reachable"
        except Exception as exc:
            return False, str(exc)

