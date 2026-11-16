"""Local Ollama provider."""

from __future__ import annotations

import requests

from src.core.exceptions import ProviderError
from src.providers.base import LLMProvider, provider_error
from src.utils.retry_utils import retry


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2", timeout: float = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate_text(self, prompt: str, *, temperature: float = 0.7) -> str:
        def call() -> str:
            response = requests.post(f"{self.base_url}/api/generate", json={"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}}, timeout=self.timeout)
            if response.status_code == 404:
                detail = response.text.strip()
                raise ProviderError(f"Ollama model '{self.model}' was not found. Run `ollama list` to see installed models, then set OLLAMA_MODEL in .env. Ollama response: {detail}")
            response.raise_for_status()
            text = response.json().get("response", "")
            if not text:
                raise ProviderError("Ollama returned an empty response")
            return text

        try:
            return retry(call, attempts=2, retry_on=(requests.ConnectionError,))
        except requests.Timeout as exc:
            raise ProviderError(f"Ollama generation timed out after {self.timeout:g} seconds. Increase OLLAMA_TIMEOUT in .env or use a smaller/faster local model. The model may still be loading or generating on CPU.") from exc
        except ProviderError:
            raise
        except Exception as exc:
            raise provider_error("Ollama", exc) from exc

    def test_connection(self) -> tuple[bool, str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            return True, f"Ollama is reachable ({self.model} selected)"
        except Exception as exc:
            return False, f"Ollama is not reachable: {exc}"

