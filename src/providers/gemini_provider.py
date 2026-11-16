"""Google Gemini provider using the official google-genai SDK."""

from __future__ import annotations

from src.core.exceptions import ProviderError
from src.providers.base import LLMProvider, provider_error
from src.utils.retry_utils import retry


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        self.require_key(api_key, "Gemini")
        self.model = model
        from google import genai

        self.client = genai.Client(api_key=api_key)

    def generate_text(self, prompt: str, *, temperature: float = 0.7) -> str:
        try:
            response = retry(lambda: self.client.models.generate_content(model=self.model, contents=prompt), attempts=3)
            text = getattr(response, "text", None)
            if not text:
                raise ProviderError("Gemini returned an empty response")
            return text
        except ProviderError:
            raise
        except Exception as exc:
            raise provider_error("Gemini", exc) from exc

    def test_connection(self) -> tuple[bool, str]:
        try:
            self.generate_text("Reply with the single word OK.", temperature=0)
            return True, f"Gemini {self.model} is reachable"
        except Exception as exc:
            return False, str(exc)

